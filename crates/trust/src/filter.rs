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
type Db<'a> = BTreeSet<Entry<'a>>;
type MetaDb<'a> = HashMap<&'a str, Metadata>;

/// Internal API
#[derive(Copy, Clone, Debug, Eq, PartialEq)]
struct Entry<'a> {
    k: &'a str,
    d: Dec,
    p: Option<&'a &'a str>,
}

impl<'a> From<(&'a str, Dec)> for Entry<'a> {
    fn from((k, d): (&'a str, Dec)) -> Self {
        Entry { k, d, p: None }
    }
}

impl Ord for Entry<'_> {
    fn cmp(&self, other: &Self) -> Ordering {
        other.k.cmp(self.k)
    }
}

impl PartialOrd for Entry<'_> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        other.k.partial_cmp(self.k)
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
struct MetaDecider<'a> {
    db: Decider<'a>,
    meta: MetaDb<'a>,
}

impl<'a> MetaDecider<'a> {
    // allow or deny
    fn check<T: AsRef<str>>(&self, p: T) -> bool {
        self.db.check(p)
    }

    // allow or deny, with meta
    fn check_ln<T: AsRef<str>>(&self, p: T) -> (bool, Meta) {
        let m = p.as_ref();
        let (d, ln) = self
            .db
            .0
            .iter()
            .find_map(|e| {
                if m.starts_with(e.k) {
                    Some((e.d, Some(e.k)))
                } else {
                    None
                }
            })
            .unwrap_or((Exc, None));

        let meta = ln
            .map(|k| self.meta.get(k))
            .flatten()
            .map(|x| LineNumber(x.0))
            .unwrap_or(Meta::Unknown);

        (d.into(), meta)
    }

    fn add_ln(&mut self, k: &'a str, d: Dec, ln: LineNum) {
        self.db.0.insert((k, d).into());
        self.meta.insert(k, Metadata(ln));
    }
}

#[derive(Default)]
struct Decider<'a>(Db<'a>);
impl<'a> Decider<'a> {
    fn make(e: (&'a str, Dec)) -> Decider<'a> {
        let mut db = Db::new();
        db.insert(e.into());
        Self(db)
    }

    // allow or deny
    fn check<T: AsRef<str>>(&self, p: T) -> bool {
        let m = p.as_ref();
        dbg!(&self.0);
        self.0
            .iter()
            .find_map(|e| if m.starts_with(e.k) { Some(e.d) } else { None })
            .unwrap_or(Exc)
            .into()
    }

    fn add(&mut self, k: &'a str, d: Dec) {
        self.0.insert((k, d).into());
    }
}

fn parse<'a>(lines: &[&'a str]) -> Result<Decider<'a>, Error> {
    let mut decider = Decider::default();

    let mut entries = vec![];
    for line in lines {
        entries.push(parse_entry(line)?);
    }

    let entries: Vec<_> = entries
        .into_iter()
        .map(|(i, (k, d))| (i, Entry { k, d, p: None }))
        .collect();

    let mut last_i = 0;
    let mut parents: Vec<&'a str> = vec![];
    for (i, mut e) in entries.iter().by_ref() {
        if *i == last_i {
            e.p = parents.last();
        } else {
            let x = parents.last();
        }
    }

    // let mut es = vec![];
    // let mut p = None;
    // let mut i = 0;
    // for (ii, (k, d)) in entries {
    //     let e = Entry { k, d, p };
    //     es.push(e);
    // }
    //
    // let mut v = vec![];
    // let mut l = None;
    // for i in 0..10 {
    //     l = v.last();
    //     v.push(i);
    // }

    Ok(decider)
}

fn parse_meta<'a>(lines: &[&'a str]) -> Result<MetaDecider<'a>, Error> {
    let mut decider = MetaDecider::default();
    for (i, line) in lines.iter().enumerate() {
        parse_entry(line).map(|(_, (k, d))| decider.add_ln(k, d, i))?;
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
