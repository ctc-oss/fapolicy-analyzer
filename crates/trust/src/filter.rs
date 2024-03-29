/*
 * Copyright Concurrent Technologies Corporation 2024
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::cell::Cell;
use std::cmp::Ordering;
use std::collections::{BTreeSet, HashMap};
use std::fmt::{Display, Formatter, Write};
use std::path::PathBuf;

use nom::branch::alt;
use nom::bytes::complete::tag;
use nom::character::complete::{space0, space1};
use nom::combinator::{complete, map, rest};
use nom::sequence::{separated_pair, tuple};
use nom::{IResult, Parser};
use thiserror::Error;

use crate::filter::Dec::*;
use crate::filter::Meta::LineNumber;

/// Internal API
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

/// Internal API
// bool == allow
impl From<Dec> for bool {
    fn from(value: Dec) -> Self {
        match value {
            Exc => false,
            Inc => true,
        }
    }
}

/// Internal API
type Db = BTreeSet<Entry>;
type MetaDb = HashMap<PathBuf, Metadata>;

/// Internal API
#[derive(Clone, Debug, Eq, PartialEq)]
struct Entry {
    k: PathBuf,
    d: Dec,
    m: usize,
    p: usize,
}

impl From<(PathBuf, Dec)> for Entry {
    fn from((k, d): (PathBuf, Dec)) -> Self {
        Entry { k, d, m: 0, p: 0 }
    }
}

impl Ord for Entry {
    fn cmp(&self, other: &Self) -> Ordering {
        other.k.cmp(&self.k)
    }
}

impl PartialOrd for Entry {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        other.k.partial_cmp(&self.k)
    }
}

type LineNum = usize;

// This could expand to more properties
// For now it will stay simple.
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
        let m: PathBuf = p.into();
        let (d, ln) = self
            .db
            .0
            .iter()
            .find_map(|e| {
                if m.starts_with(e.k.clone()) {
                    Some((e.d, Some(e.k.clone())))
                } else {
                    None
                }
            })
            .unwrap_or((Exc, None));

        let meta = ln
            .as_ref()
            .map(|k| self.meta.get(k))
            .flatten()
            .map(|x| LineNumber(x.0))
            .unwrap_or(Meta::Unknown);

        (d.into(), meta)
    }

    fn add_ln(&mut self, k: PathBuf, d: Dec, ln: LineNum) {
        self.db.0.insert((k.clone(), d).into());
        self.meta.insert(k, Metadata(ln));
    }
}

#[derive(Default)]
struct Decider(Db);
impl<'a> Decider {
    fn make((k, v): (&str, Dec)) -> Decider {
        let mut db = Db::new();
        db.insert((k.into(), v).into());
        Self(db)
    }

    // allow or deny
    fn check(&self, p: &str) -> bool {
        let m: PathBuf = p.into();
        dbg!(&self.0);
        self.0
            .iter()
            .find_map(|e| {
                if m.starts_with(e.k.clone()) {
                    Some(e.d)
                } else {
                    None
                }
            })
            .unwrap_or(Exc)
            .into()
    }

    fn add(&mut self, k: PathBuf, d: Dec) {
        self.0.insert((k, d).into());
    }
}

fn parse(lines: &[&str]) -> Result<Decider, Error> {
    let mut decider = Decider::default();

    let mut prev_i = None;
    let mut stack = vec![];
    for line in lines {
        match (prev_i, parse_entry(line)) {
            (None, Ok((i, (k, d)))) if i == 0 => {
                let p = PathBuf::from(k);
                println!("a push [{}{p:?}]", " ".repeat(i));
                stack.push(p);
                prev_i = Some(i);
                decider.add(k.into(), d);
            }
            (Some(pi), Ok((i, (k, d)))) if i == 0 => {
                let p = PathBuf::from(k);
                println!("a2 push [{}{p:?}]", " ".repeat(i));
                stack.push(p.clone());
                prev_i = Some(0);
                decider.add(p, d);
            }
            (None, Ok((i, (k, d)))) => {
                panic!("bad format too many start indent")
            }
            (Some(pi), Ok((i, (k, d)))) if i > pi => {
                let last = stack.last().unwrap();
                let p = last.join(k);
                println!("b push [{d}{p:?}]");
                stack.push(p.clone());
                prev_i = Some(i);
                decider.add(p, d);
            }
            (Some(pi), Ok((i, (k, d)))) if i < pi => {
                let p = PathBuf::from(k);
                println!("c push [{}{p:?}]", " ".repeat(i));
                stack.push(p.clone());
                prev_i = Some(i);
                decider.add(p, d);
            }
            (Some(pi), Ok((i, (k, d)))) => {
                println!("d push ");
            }
            (_, Err(_)) => eprintln!("failed ot parse"),
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

#[derive(Error, Debug)]
enum Error {
    #[error("Malformed Dec decl")]
    MalformedDec,
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
    .map_err(|_| Error::MalformedDec)
}

#[cfg(test)]
mod tests {
    use crate::filter::Dec::*;
    use crate::filter::Meta::*;
    use crate::filter::{parse, parse_entry, parse_meta, Decider, Error, MetaDecider};
    use assert_matches::assert_matches;

    #[test]
    fn test_parser() -> Result<(), Error> {
        let (i, (k, d)) = parse_entry("          + foo")?;
        println!("{i} -> {d} {k}");
        Ok(())
    }

    #[test]
    fn test_indented() -> Result<(), Error> {
        let s = " ";
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
}

// .nf
// .B # this is simple allow list
// .B - /usr/bin/some_binary1
// .B - /usr/bin/some_binary2
// .B + /
// .fi
//
// .nf
// .B # this is the same
// .B + /
// .B \ + usr/bin/
// .B \ \ - some_binary1
// .B \ \ - some_binary2
// .fi
//
// .nf
// .B # this is similar allow list with a wildcard
// .B - /usr/bin/some_binary?
// .B + /
// .fi
//
// .nf
// .B # this is similar with another wildcard
// .B + /
// .B \ - usr/bin/some_binary*
// .fi
//
// .nf
// .B # keeps everything except usr/share except python and perl files
// .B # /usr/bin/ls - result is '+'
// .B # /usr/share/something - result is '-'
// .B # /usr/share/abcd.py - result is '+'
// .B + /
// .B \ - usr/share/
// .B \ \ + *.py
// .B \ \ + *.pl
// .fi
//
//----------
//
// # default filter file for fedora
//
// + /
//  - usr/include/
//  - usr/share/
//   # Python byte code
//   + *.py?
//   # Python text files
//   + *.py
//   # Some apps have a private libexec
//   + */libexec/*
//   # Ruby
//   + *.rb
//   # Perl
//   + *.pl
//   # System tap
//   + *.stp
//   # Javascript
//   + *.js
//   # Java archive
//   + *.jar
//   # M4
//   + *.m4
//   # PHP
//   + *.php
//   # Perl Modules
//   + *.pm
//   # Lua
//   + *.lua
//   # Java
//   + *.class
//   # Typescript
//   + *.ts
//   # Typescript JSX
//   + *.tsx
//   # Lisp
//   + *.el
//   # Compiled Lisp
//   + *.elc
//  - usr/src/kernel*/
//   + */scripts/*
//   + */tools/objtool/*
