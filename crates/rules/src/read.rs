/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::path::PathBuf;

use nom::branch::alt;
use nom::character::complete::multispace0;
use nom::combinator::{eof, map, recognize};
use nom::error::{ErrorKind, ParseError};
use nom::sequence::tuple;

use crate::db::{Entry, DB};
use crate::error::Error;
use crate::linter::lint::lint_db;
use crate::load::RuleFrom::{Disk, Mem};
use crate::load::RuleSource;
use crate::parser::parse::{StrTrace, TraceResult};
use crate::parser::{comment, rule, set};
use crate::read::Line::*;
use crate::{load, Rule, Set};

#[derive(Debug)]
enum Line {
    Blank,
    Comment(String),
    SetDef(Set),
    RuleDef(Rule),
    Malformed(String, String),
    MalformedSet(String, String),
}

enum LineError<I> {
    CannotParseSet(I, String),
    CannotParse(I, String),
    Nom(I, ErrorKind),
}

impl<I> ParseError<I> for LineError<I> {
    fn from_error_kind(input: I, kind: ErrorKind) -> Self {
        LineError::Nom(input, kind)
    }

    fn append(_: I, _: ErrorKind, other: Self) -> Self {
        other
    }
}

fn parser(i: &str) -> nom::IResult<StrTrace, Line, LineError<&str>> {
    alt((
        map(blank_line, |_| Blank),
        map(comment::parse, Comment),
        map(set::parse, SetDef),
        map(rule::parse, RuleDef),
    ))(StrTrace::new(i))
    .map_err(|e| {
        let details = match e {
            nom::Err::Error(e) => e.to_string(),
            e => format!("{:?}", e),
        };
        // todo;; guess set or rule here based on the line start char?
        let f = if i.starts_with('%') {
            LineError::CannotParseSet
        } else {
            LineError::CannotParse
        };

        nom::Err::Error(f(i, details))
    })
}

fn blank_line(i: StrTrace) -> TraceResult<StrTrace> {
    recognize(tuple((multispace0, eof)))(i)
}

pub fn deserialize_rules_db(text: &str) -> Result<DB, Error> {
    read_rules_db(load::rules_from(Mem(text.to_string()))?)
}

pub fn load_rules_db(path: &str) -> Result<DB, Error> {
    read_rules_db(load::rules_from(Disk(PathBuf::from(path)))?)
}

fn read_rules_db(xs: Vec<RuleSource>) -> Result<DB, Error> {
    let lookup: Vec<(String, Entry)> = xs
        .iter()
        .map(|(p, s)| {
            (
                // render and split off the filename from full path
                p.display()
                    .to_string()
                    .rsplit_once('/')
                    .map(|(_, rhs)| rhs.to_string())
                    // if there was no / separator then use the full path
                    .unwrap_or_else(|| p.display().to_string()),
                s,
            )
        })
        .map(|(source, l)| (source, parser(l)))
        .flat_map(|(source, r)| match r {
            Ok((t, rule)) if t.current.is_empty() => Some((source, rule)),
            Ok((_, _)) => None,
            Err(nom::Err::Error(LineError::CannotParse(i, why))) => {
                Some((source, Malformed(i.to_string(), why)))
            }
            Err(nom::Err::Error(LineError::CannotParseSet(i, why))) => {
                Some((source, MalformedSet(i.to_string(), why)))
            }
            Err(_) => None,
        })
        .filter_map(|(source, line)| match line {
            RuleDef(r) => Some((source, Entry::ValidRule(r))),
            SetDef(s) => Some((source, Entry::ValidSet(s))),
            Malformed(text, error) => Some((source, Entry::Invalid { text, error })),
            MalformedSet(text, error) => Some((source, Entry::InvalidSet { text, error })),
            _ => None,
        })
        .collect();

    Ok(lint_db(DB::from_sources(lookup)))
}
