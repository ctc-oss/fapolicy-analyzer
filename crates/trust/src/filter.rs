/*
 * Copyright Concurrent Technologies Corporation 2024
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::collections::HashMap;
use std::fmt::{Display, Formatter};
use std::path::PathBuf;

use nom::branch::alt;
use nom::bytes::complete::tag;
use nom::character::complete::{space0, space1};
use nom::combinator::{complete, map, rest};
use nom::sequence::{separated_pair, tuple};
use nom::IResult;
use thiserror::Error;

use crate::filter::Dec::*;

#[derive(Error, Debug)]
pub enum Error {
    #[error("Malformed: {0}")]
    MalformedDec(String),

    #[error("Malformed: root element is not absolute")]
    NonAbsRootElement,

    #[error("Malformed: too many starting indents")]
    TooManyStartIndents,
}

#[derive(Copy, Clone, Debug, Default, Eq, PartialEq)]
enum Dec {
    #[default]
    Exc,
    Inc,
}

impl Display for Dec {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Exc => f.write_str("-"),
            Inc => f.write_str("+"),
        }
    }
}

impl From<Dec> for bool {
    fn from(value: Dec) -> Self {
        match value {
            Exc => false,
            Inc => true,
        }
    }
}

type Db = Node;
type MetaDb = HashMap<String, Metadata>;

#[derive(Debug, Default)]
struct Node {
    children: HashMap<char, Node>,
    decision: Option<Dec>,
}

impl Node {
    pub fn add(&mut self, path: &str, d: Dec) {
        let mut node = self;
        for c in path.chars() {
            node = node.children.entry(c).or_insert_with(Node::default);
        }
        node.decision = Some(d);
    }

    pub fn check(&self, path: &str) -> Dec {
        self.find(path, 0, false).unwrap_or(Exc)
    }

    fn find(&self, path: &str, idx: usize, wc: bool) -> Option<Dec> {
        if idx == path.len() {
            return match self.decision {
                d @ Some(_) => d,
                None => {
                    if self.children.contains_key(&'*')
                        && self
                            .children
                            .iter()
                            .find_map(|(c, _)| if *c == '*' { Some(Inc) } else { None })
                            .is_none()
                    {
                        Some(Inc)
                    } else {
                        None
                    }
                }
            };
        }

        let c = path.chars().nth(idx).unwrap();

        // try to find a node matching the next char
        if let Some(node) = self.children.get(&c) {
            if let Some(d) = node.find(path, idx + 1, false) {
                return Some(d);
            }
        }
        // next try to find a wildcard char
        else if let Some(wc) = self.children.get(&'?') {
            if let Some(d) = wc.find(path, idx + 1, true) {
                return Some(d);
            }
        }

        // a wildcard leaf provides the decision
        // a wildcard node needs traversed
        if let Some(star_node) = self.children.get(&'*') {
            return match star_node.decision {
                None => {
                    // not a leaf node;; step through children of wildcard
                    if let Some(r) = star_node.find(path, idx, true) {
                        Some(r)
                    } else {
                        self.find(path, idx + 1, wc)
                    }
                }
                // leaf nodes propagate their decision
                leaf_decision => leaf_decision,
            };
        }

        if wc {
            None
        } else {
            self.decision
        }
    }
}

type LineNum = usize;

#[derive(Default)]
struct Metadata(LineNum);

/// Public API
#[derive(Debug)]
enum Meta {
    Unknown,
    LineNumber(LineNum),
}

/// Internal API
#[derive(Default)]
struct MetaDecider {
    db: Decider,
    meta: MetaDb,
}

impl<'a> MetaDecider {
    // allow or deny
    fn check(&self, p: &str) -> bool {
        self.db.check(p)
    }

    // allow or deny, with meta
    fn check_ln(&self, p: &str) -> (bool, Meta) {
        let d = self.check(p);
        (d, Meta::Unknown)
    }

    fn add_ln(&mut self, k: &str, d: Dec, ln: LineNum) {
        self.db.add(k, d);
        self.meta.insert(k.to_owned(), Metadata(ln));
    }
}

#[derive(Debug, Default)]
struct Decider(Db);
impl<'a> Decider {
    fn make((k, d): (&str, Dec)) -> Decider {
        let mut db = Db::default();
        db.add(k, d);
        Self(db)
    }

    // allow or deny
    fn check(&self, p: &str) -> bool {
        self.0.check(p) == Inc
    }

    fn add(&mut self, k: &str, d: Dec) {
        self.0.add(k, d);
    }
}

fn ignored_line(l: &str) -> bool {
    l.trim_start().starts_with('#') || l.trim().is_empty()
}

fn parse(lines: &[&str]) -> Result<Decider, Error> {
    use Error::*;

    let mut decider = Decider::default();

    let mut prev_i = None;
    let mut stack = vec![];
    for line in lines.iter().filter(|x| !ignored_line(x)) {
        match (prev_i, parse_entry(line)) {
            (None, Ok((i, (k, d)))) if i == 0 => {
                if !k.starts_with('/') {
                    return Err(NonAbsRootElement);
                }
                let p = PathBuf::from(k);
                stack.push(p);
                prev_i = Some(i);
                decider.add(k.into(), d);
            }
            (None, Ok((_, (_, _)))) => return Err(TooManyStartIndents),
            (Some(_), Ok((i, (k, d)))) if i == 0 => {
                if !k.starts_with('/') {
                    return Err(NonAbsRootElement);
                }
                let p = PathBuf::from(k);
                stack.push(p.clone());
                prev_i = Some(0);
                decider.add(&p.display().to_string(), d);
            }
            (Some(pi), Ok((i, (k, d)))) if i > pi => {
                let last = stack.last().unwrap();
                let p = last.join(k);
                stack.push(p.clone());
                prev_i = Some(i);
                decider.add(&p.display().to_string(), d);
            }
            (Some(pi), Ok((i, (k, d)))) if i < pi => {
                stack.truncate(i);
                let last = stack.last().unwrap();
                let p = last.join(k);
                stack.push(p.clone());
                prev_i = Some(i);
                decider.add(&p.display().to_string(), d);
            }
            (Some(_), Ok((i, (k, d)))) => {
                stack.truncate(i);
                let last = stack.last().unwrap();
                let p = last.join(k);
                stack.push(p.clone());
                decider.add(&p.display().to_string(), d);
            }
            (_, Err(_)) => return Err(MalformedDec(line.to_string())),
        }
    }

    Ok(decider)
}

fn parse_meta(lines: &[&str]) -> Result<MetaDecider, Error> {
    let mut decider = MetaDecider::default();
    for (i, line) in lines.iter().enumerate() {
        parse_entry(line).map(|(_, (k, d))| decider.add_ln(k.into(), d, i))?;
    }
    Ok(decider)
}

fn parse_dec(i: &str) -> IResult<&str, Dec> {
    alt((map(tag("+"), |_| Inc), map(tag("-"), |_| Exc)))(i)
}

fn parse_entry(i: &str) -> Result<(usize, (&str, Dec)), Error> {
    complete(tuple((
        map(space0, |s: &str| s.len()),
        separated_pair(parse_dec, space1, rest),
    )))(i)
    .map(|(_, (indent, (d, p)))| (indent, (p, d)))
    .map_err(|_| Error::MalformedDec(i.to_string()))
}

#[cfg(test)]
mod tests {
    use assert_matches::assert_matches;
    use fapolicy_util::trimto::TrimTo;

    use crate::filter::Dec::*;
    use crate::filter::Meta::*;
    use crate::filter::{parse, parse_meta, Decider, Error, MetaDecider};

    #[test]
    fn test_too_many_indents() {
        assert_matches!(parse(&[" + foo"]), Err(Error::TooManyStartIndents));
    }

    #[test]
    fn test_i0_starts_with_slash() {
        assert_matches!(parse(&["+ x"]), Err(Error::NonAbsRootElement));
        assert_matches!(
            parse(&["+ /", " - foo", "+ bar"]),
            Err(Error::NonAbsRootElement)
        );
    }

    #[test]
    fn test_indented() -> Result<(), Error> {
        let d = parse(&["+ /", " - b", "  + baz"])?;
        //                             _     _       __
        assert!(d.check("/a"));
        assert!(!d.check("/b"));
        assert!(d.check("/b/baz"));
        assert!(!d.check("/b/bar"));
        Ok(())
    }

    #[test]
    fn test_mix_indented() -> Result<(), Error> {
        let d = parse(&["+ /", "  - foo/bar", "   + baz"])?;
        //                             _     __             ___
        assert!(d.check("/"));
        assert!(d.check("/foo"));
        assert!(!d.check("/foo/bar"));
        assert!(!d.check("/foo/bar/biz"));
        assert!(d.check("/foo/bar/baz"));
        Ok(())
    }

    #[test]
    fn test_nested() -> Result<(), Error> {
        let d = parse(&["+ /", "- /foo/bar", "+ /foo/bar/baz"])?;
        assert!(d.check("/"));
        assert!(d.check("/foo"));
        assert!(!d.check("/foo/bar"));
        assert!(!d.check("/foo/bar/biz"));
        assert!(d.check("/foo/bar/baz"));
        Ok(())
    }

    #[test]
    fn test_multi() -> Result<(), Error> {
        let d = parse(&["+ /", "- /foo"])?;
        assert!(d.check("/"));
        assert!(!d.check("/foo"));
        Ok(())
    }

    #[test]
    fn test_q_wildcard() -> Result<(), Error> {
        let d = parse(&["+ /", " - b?"])?;
        //                             _     _       __
        assert!(d.check("/a"));
        assert!(d.check("/b"));
        assert!(!d.check("/bb"));
        assert!(!d.check("/bc"));
        assert!(d.check("/bcd"));
        Ok(())
    }

    #[test]
    fn test_star_wildcard() -> Result<(), Error> {
        let d = parse(&["+ /", " - b", " - b*"])?;
        //                             _     _       __
        assert!(d.check("/a"));
        assert!(!d.check("/b"));
        assert!(!d.check("/bb"));
        assert!(!d.check("/bc"));
        assert!(!d.check("/bcd"));
        Ok(())
    }

    #[test]
    fn test_multi_meta() -> Result<(), Error> {
        let d = parse_meta(&["+ /", "- /foo"])?;
        assert!(d.check("/"));
        assert!(!d.check("/foo"));
        assert_matches!(d.check_ln("/"), (true, LineNumber(0)));
        assert_matches!(d.check_ln("/foo"), (false, LineNumber(1)));
        Ok(())
    }

    #[test]
    fn test_parse() -> Result<(), Error> {
        let d = parse(&["+ /"])?;
        assert!(d.check("/"));
        assert!(d.check("/foo"));

        let d = parse(&["+ /foo"])?;
        assert!(!d.check("/"));
        assert!(d.check("/foo"));
        Ok(())
    }

    #[test]
    fn test_parse_unnest() {
        let al = r#"
        |+ /
        | - usr/foo
        |   + *.py
        | - usr/bar
        |   + *.py
        | "#
        .trim_to('|');

        let d = parse(&al.split("\n").collect::<Vec<&str>>()).unwrap();
        assert!(!d.check("/usr/foo/x"));
        assert!(d.check("/usr/foo/x.py"));
        assert!(!d.check("/usr/bar/x"));
        assert!(d.check("/usr/foo/x.py"));
    }

    #[test]
    fn test_next() {
        let d = Decider::make(("/", Inc));
        assert!(d.check("/"));
        assert!(d.check("/foo"));

        let d = Decider::make(("/foo", Inc));
        assert!(!d.check("/"));
        assert!(d.check("/foo"));
    }

    // an empty decider should deny everything
    #[test]
    fn test_frist() {
        let d = Decider::default();
        assert!(!d.check("/"));
        assert!(!d.check("/foo"));
    }

    #[test]
    fn test_frist_meta() {
        // the plain old check should work
        let d = MetaDecider::default();
        assert!(!d.check("/"));
        assert!(!d.check("/foo"));

        // the meta check would return unknown on empty decider
        assert_matches!(d.check_ln("/"), (false, Unknown))
    }

    #[test]
    fn simple_allow_list1() {
        let al = r#"
        |- /usr/bin/some_binary1
        |- /usr/bin/some_binary2
        |+ /"#
            .trim_to('|');

        let d = parse(&al.split("\n").collect::<Vec<&str>>()).unwrap();
        assert!(d.check("/"));
        assert!(!d.check("/usr/bin/some_binary1"));
        assert!(!d.check("/usr/bin/some_binary2"));
    }

    #[test]
    fn simple_allow_list2() {
        let al = r#"
        |+ /
        | + usr/bin/
        |  - some_binary1
        |  - some_binary2"#
            .trim_to('|');

        let d = parse(&al.split("\n").collect::<Vec<&str>>()).unwrap();
        assert!(d.check("/"));
        assert!(!d.check("/usr/bin/some_binary1"));
        assert!(!d.check("/usr/bin/some_binary2"));
    }

    #[test]
    fn simple_allow_list_wc1() {
        let al = r#"
        |- /usr/bin/some_binary?
        |+ /"#
            .trim_to('|');

        let d = parse(&al.split("\n").collect::<Vec<&str>>()).unwrap();
        assert!(d.check("/"));
        assert!(!d.check("/usr/bin/some_binary1"));
        assert!(!d.check("/usr/bin/some_binary2"));
    }

    #[test]
    fn simple_allow_list_wc2() {
        let al = r#"
        |+ /
        | - usr/bin/some_binary*"#
            .trim_to('|');

        let d = parse(&al.split("\n").collect::<Vec<&str>>()).unwrap();
        assert!(d.check("/"));
        assert!(!d.check("/usr/bin/some_binary1"));
        assert!(!d.check("/usr/bin/some_binary2"));
    }

    #[test]
    fn simple_allow_list_wc3() {
        let al = r#"
        |+ /
        | - usr/share
        |  + *.py
        |  + *.pl"#
            .trim_to('|');

        let d = parse(&al.split("\n").collect::<Vec<&str>>()).unwrap();
        assert!(d.check("/usr/bin/ls"));
        assert!(!d.check("/usr/share/something"));
        assert!(d.check("/usr/share/abcd.py"));
    }

    #[test]
    fn simple_allow_list_wc4() {
        let al = r#"
        |+ /
        | - usr/share
        |   + *.py"#
            .trim_to('|');

        let d = parse(&al.split("\n").collect::<Vec<&str>>()).unwrap();
        assert!(!d.check("/usr/share/abc"));
        // assert!(!d.check("/usr/share/abc.py"));
    }

    #[test]
    fn simple_allow_list_wc5() {
        let al = r#"
        |+ /
        | - usr/share
        |   + *.py"#
            .trim_to('|');

        let d = parse(&al.split("\n").collect::<Vec<&str>>()).unwrap();
        assert!(!d.check("/usr/share/abc"));
        assert!(!d.check("/usr/share/abc.pl"));
        assert!(d.check("/usr/share/abc.py"));
    }

    #[test]
    fn test_default_filter_file_for_fedora() {
        let al = r#"
        |+ /
        | - usr/include/
        | - usr/share/
        |  # Python byte code
        |  + *.py?
        |  # Python text files
        |  + *.py
        |  # Some apps have a private libexec
        |  + */libexec/*
        |  # Ruby
        |  + *.rb
        |  # Perl
        |  + *.pl
        |  # System tap
        |  + *.stp
        |  # Javascript
        |  + *.js
        |  # Java archive
        |  + *.jar
        |  # M4
        |  + *.m4
        |  # PHP
        |  + *.php
        |  # Perl Modules
        |  + *.pm
        |  # Lua
        |  + *.lua
        |  # Java
        |  + *.class
        |  # Typescript
        |  + *.ts
        |  # Typescript JSX
        |  + *.tsx
        |  # Lisp
        |  + *.el
        |  # Compiled Lisp
        |  + *.elc
        | - usr/src/kernel*/
        |  + */scripts/*
        |  + */tools/objtool/*

        |"#
        .trim_to('|');

        let d = parse(&al.split("\n").collect::<Vec<&str>>()).unwrap();
        assert!(d.check("/bin/foo"));
        assert!(!d.check("/usr/share/x.txt"));
        assert!(!d.check("/usr/include/x.h"));
        assert!(d.check("/usr/share/python/my.py"));
        assert!(d.check("/usr/share/python/my.pyc"));
        assert!(!d.check("/usr/share/python/my.foo"));
        assert!(d.check("/usr/share/myapp/libexec/anything"));
        assert!(!d.check("/usr/share/myapp2/not-libexec/anything"));
        assert!(!d.check("/usr/src/kernel/foo"));
        assert!(!d.check("/usr/src/kernel-6.5/foo"));
        assert!(d.check("/usr/src/kernels/5.13.16/scripts/foo"));
        assert!(d.check("/usr/src/kernels/5.13.16/tools/objtool/foo"));
    }

    #[test]
    fn test_from_nested_back_to_0() {
        let al = r#"
        |+ /
        | - usr/share/
        |  + abc/def/
        |   + *.py
        |- /tmp/x
        |- /tmp/y
        |- /z"#
            .trim_to('|');

        let d = parse(&al.split("\n").collect::<Vec<&str>>()).unwrap();
        assert!(!d.check("/usr/share/xyz"));
        assert!(d.check("/usr/share/abc/def/foo.py"));
        assert!(!d.check("/tmp/x"));
        assert!(!d.check("/tmp/y"));
        assert!(!d.check("/z"));
    }
}
