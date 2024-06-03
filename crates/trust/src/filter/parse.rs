/*
 * Copyright Concurrent Technologies Corporation 2024
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::collections::HashMap;
use std::default::Default;
use std::path::{Path, PathBuf};

use nom::branch::alt;
use nom::bytes::complete::tag;
use nom::character::complete::{space0, space1};
use nom::combinator::{complete, map, rest};
use nom::sequence::{separated_pair, tuple};
use nom::IResult;
use thiserror::Error;

use crate::filter::parse::Dec::*;

/// Errors that can occur in this module
#[derive(Error, Debug)]
pub enum Error {
    #[error("Malformed: {0}")]
    MalformedDec(String),

    #[error("Malformed: root element is not absolute")]
    NonAbsRootElement,

    #[error("Malformed: too many starting indents")]
    TooManyStartIndents,
}

type LineNum = usize;

/// Represents a filter decision about whether a path should be
/// included or excluded from the trust database
#[derive(Copy, Clone, Debug, Default, Eq, PartialEq)]
pub enum Dec {
    /// The default decision made due to lack of explicit config
    #[default]
    Default,
    /// Exclude, contains the source line number
    Exc(LineNum),
    /// Include, contains the source line number
    Inc(LineNum),
}

impl Dec {
    fn with_line_num(self, ln: LineNum) -> Self {
        match self {
            Default | Exc(_) => Exc(ln),
            Inc(_) => Inc(ln),
        }
    }

    fn is_explicit(&self) -> bool {
        matches!(self, Inc(_) | Exc(_))
    }
}

/// Makes filter policy decisions against a path
/// Built from a parse of a filter conf
#[derive(Debug, Default)]
pub struct Decider(Node);
impl Decider {
    pub fn check(&self, p: &str) -> bool {
        matches!(self.0.check(p), Inc(_))
    }

    pub fn dec(&self, p: &str) -> Dec {
        self.0.check(p)
    }

    pub fn add<P: AsRef<Path>>(&mut self, k: P, d: Dec) {
        self.0.add(k, d);
    }
}

enum Wild {
    // exactly once
    Single,
    // 1 or more
    Glob,
}

// A trie structure that maps filter path chars to nodes
// The end of word is marked by a decision being present
#[derive(Debug, Default)]
struct Node {
    children: HashMap<char, Node>,
    decision: Option<Dec>,
}

impl Node {
    pub fn add<P: AsRef<Path>>(&mut self, path: P, d: Dec) {
        assert!(d.is_explicit());
        let mut node = self;
        for c in path.as_ref().display().to_string().chars() {
            node = node.children.entry(c).or_default();
        }
        node.decision = Some(d);
    }

    /// Check a path against the filter
    pub fn check<P: AsRef<Path>>(&self, path: P) -> Dec {
        self.find(path.as_ref().display().to_string().as_ref(), 0, None)
            .unwrap_or(Default)
    }

    // recurse the trie with wildcard support
    fn find(&self, path: &str, idx: usize, wild: Option<Wild>) -> Option<Dec> {
        if idx == path.len() {
            return self.decision;
        }
        let c = path.chars().nth(idx).unwrap();

        // try to find a node matching the char
        if let Some(node) = self.children.get(&c) {
            if let Some(d) = node.find(path, idx + 1, None) {
                return Some(d);
            }
        }
        // if no match check for a single wildcard char
        else if let Some(wc) = self.children.get(&'?') {
            if let Some(d) = wc.find(path, idx + 1, Some(Wild::Single)) {
                return Some(d);
            }
        }
        // or a glob: leaves provide the decision, a node needs traversed
        else if let Some(star_node) = self.children.get(&'*') {
            return match star_node.decision {
                None => star_node
                    .find(path, idx, Some(Wild::Glob))
                    .or_else(|| self.find(path, idx + 1, wild)),
                leaf_decision => leaf_decision,
            };
        }

        // a match while wild defers decision to the parent
        match wild {
            Some(_) => None,
            None => self.decision,
        }
    }
}

fn ignored_line(l: &str) -> bool {
    l.trim_start().starts_with('#') || l.trim().is_empty()
}

/// Parse a filter config from the conf lines
pub fn parse(lines: &[&str]) -> Result<Decider, Error> {
    use Error::*;

    let mut decider = Decider::default();

    let mut prev_i = None;
    let mut stack = vec![];

    // process lines from the config, ignoring comments and empty lines
    for (ln, line) in lines.iter().enumerate().filter(|(_, x)| !ignored_line(x)) {
        match (prev_i, parse_entry(line)) {
            // ensure root level starts with /
            (_, Ok((0, (k, _)))) if !k.starts_with('/') => return Err(NonAbsRootElement),
            // at the root level, anywhere in the conf
            (prev, Ok((0, (k, d)))) => {
                if prev.is_some() {
                    stack.clear();
                }
                decider.add(k, d.with_line_num(ln));
                stack.push(PathBuf::from(k));
                prev_i = Some(0);
            }
            // fail if the first conf element is indented
            (None, Ok((_, (_, _)))) => return Err(TooManyStartIndents),
            // handle an indentation
            (Some(pi), Ok((i, (k, d)))) if i > pi => {
                let p = stack.last().map(|l| l.join(k)).unwrap();
                decider.add(&p, d.with_line_num(ln));
                stack.push(p);
                prev_i = Some(i);
            }
            // handle unindentation
            (Some(pi), Ok((i, (k, d)))) if i < pi => {
                stack.truncate(i);
                let p = stack.last().map(|l| l.join(k)).unwrap();
                decider.add(&p, d.with_line_num(ln));
                stack.push(p);
                prev_i = Some(i);
            }
            // remaining at previous level
            (Some(_), Ok((i, (k, d)))) => {
                stack.truncate(i);
                let p = stack.last().map(|l| l.join(k)).unwrap();
                decider.add(&p, d.with_line_num(ln));
                stack.push(p);
            }
            // propagate parse errors
            (_, Err(_)) => return Err(MalformedDec(line.to_string())),
        }
    }
    Ok(decider)
}

fn parse_dec(i: &str) -> IResult<&str, Dec> {
    alt((map(tag("+"), |_| Inc(0)), map(tag("-"), |_| Exc(0))))(i)
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
    use std::default::Default;

    use crate::filter::parse::Dec::*;
    use crate::filter::parse::{parse, Decider, Error};

    // the first few tests are modeled after example config from the fapolicyd documentation

    #[test]
    fn simple_allow_list1() {
        let al = r#"
        |- /usr/bin/some_binary1
        |- /usr/bin/some_binary2
        |+ /"#
            .trim_to('|');

        let d = parse(&al.split('\n').collect::<Vec<&str>>()).unwrap();
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

        let d = parse(&al.split('\n').collect::<Vec<&str>>()).unwrap();
        assert!(d.check("/"));
        assert!(!d.check("/usr/bin/some_binary1"));
        assert!(!d.check("/usr/bin/some_binary2"));
    }

    // this one has embedded comments
    #[test]
    fn default_filter_file_for_fedora() {
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

        let d = parse(&al.split('\n').collect::<Vec<&str>>()).unwrap();
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

    // the remainder of the tests exercise other corners of the decision api

    #[test]
    fn meta_source_line_numbers() {
        let al = r#"
        |- /usr/bin/some_binary1
        |- /usr/bin/some_binary2
        |+ /
        | - foo
        | - bar/baz"#
            .trim_to('|');

        let d = parse(&al.split('\n').collect::<Vec<&str>>()).unwrap();
        assert_matches!(d.dec("/"), Inc(3));
        assert_matches!(d.dec("/usr/bin/some_binary1"), Exc(1));
        assert_matches!(d.dec("/usr/bin/some_binary2"), Exc(2));
        assert_matches!(d.dec("/foo"), Exc(4));
        assert_matches!(d.dec("/bar/baz"), Exc(5));
    }

    #[test]
    fn too_many_indents() {
        assert_matches!(parse(&[" + foo"]), Err(Error::TooManyStartIndents));
    }

    #[test]
    fn indentation_0_starts_with_slash() {
        assert_matches!(parse(&["+ x"]), Err(Error::NonAbsRootElement));
        assert_matches!(
            parse(&["+ /", " - foo", "+ bar"]),
            Err(Error::NonAbsRootElement)
        );
    }

    #[test]
    fn indentation_basic() -> Result<(), Error> {
        let d = parse(&["+ /", " - b", "  + baz"])?;
        assert!(d.check("/a"));
        assert!(!d.check("/b"));
        assert!(d.check("/b/baz"));
        assert!(!d.check("/b/bar"));
        Ok(())
    }

    #[test]
    fn indentation_mix() -> Result<(), Error> {
        let d = parse(&["+ /", "  - foo/bar", "   + baz"])?;
        assert!(d.check("/"));
        assert!(d.check("/foo"));
        assert!(!d.check("/foo/bar"));
        assert!(!d.check("/foo/bar/biz"));
        assert!(d.check("/foo/bar/baz"));
        Ok(())
    }

    #[test]
    fn indentation_nested() -> Result<(), Error> {
        let d = parse(&["+ /", "- /foo/bar", "+ /foo/bar/baz"])?;
        assert!(d.check("/"));
        assert!(d.check("/foo"));
        assert!(!d.check("/foo/bar"));
        assert!(!d.check("/foo/bar/biz"));
        assert!(d.check("/foo/bar/baz"));
        Ok(())
    }

    #[test]
    fn basic() -> Result<(), Error> {
        let d = parse(&["+ /", "- /foo"])?;
        assert!(d.check("/"));
        assert!(!d.check("/foo"));
        Ok(())
    }

    #[test]
    fn wildcard_single() -> Result<(), Error> {
        let d = parse(&["+ /", " - b?"])?;
        assert!(d.check("/a"));
        assert!(d.check("/b"));
        assert!(!d.check("/bb"));
        assert!(!d.check("/bc"));
        assert!(d.check("/bcd"));
        Ok(())
    }

    #[test]
    fn wildcard_glob() -> Result<(), Error> {
        let d = parse(&["+ /", " - b", " - b*"])?;
        assert!(d.check("/a"));
        assert!(!d.check("/b"));
        assert!(!d.check("/bb"));
        assert!(!d.check("/bc"));
        assert!(!d.check("/bcd"));
        Ok(())
    }

    #[test]
    fn parse_basic() -> Result<(), Error> {
        let d = parse(&["+ /"])?;
        assert!(d.check("/"));
        assert!(d.check("/foo"));

        let d = parse(&["+ /foo"])?;
        assert!(!d.check("/"));
        assert!(d.check("/foo"));
        Ok(())
    }

    #[test]
    fn parse_unnesting() {
        let al = r#"
        |+ /
        | - usr/foo
        |   + *.py
        | - usr/bar
        |   + *.py
        | "#
        .trim_to('|');

        let d = parse(&al.split('\n').collect::<Vec<&str>>()).unwrap();
        assert!(!d.check("/usr/foo/x"));
        assert!(d.check("/usr/foo/x.py"));
        assert!(!d.check("/usr/bar/x"));
        assert!(d.check("/usr/foo/x.py"));
    }

    // an empty decider should deny everything
    #[test]
    fn no_rules() {
        let d = Decider::default();
        assert!(!d.check("/"));
        assert!(!d.check("/foo"));
    }

    #[test]
    fn simple_allow_list_wc1() {
        let al = r#"
        |- /usr/bin/some_binary?
        |+ /"#
            .trim_to('|');

        let d = parse(&al.split('\n').collect::<Vec<&str>>()).unwrap();
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

        let d = parse(&al.split('\n').collect::<Vec<&str>>()).unwrap();
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

        let d = parse(&al.split('\n').collect::<Vec<&str>>()).unwrap();
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

        let d = parse(&al.split('\n').collect::<Vec<&str>>()).unwrap();
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

        let d = parse(&al.split('\n').collect::<Vec<&str>>()).unwrap();
        assert!(!d.check("/usr/share/abc"));
        assert!(!d.check("/usr/share/abc.pl"));
        assert!(d.check("/usr/share/abc.py"));
    }

    #[test]
    fn from_nested_back_to_0() {
        let al = r#"
        |+ /
        | - usr/share/
        |  + abc/def/
        |   + *.py
        |- /tmp/x
        |- /tmp/y
        |- /z"#
            .trim_to('|');

        let d = parse(&al.split('\n').collect::<Vec<&str>>()).unwrap();
        assert!(!d.check("/usr/share/xyz"));
        assert!(d.check("/usr/share/abc/def/foo.py"));
        assert!(!d.check("/tmp/x"));
        assert!(!d.check("/tmp/y"));
        assert!(!d.check("/z"));
    }
}
