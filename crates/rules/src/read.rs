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

use crate::db::{RuleDef, DB};
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
    WellFormedRule(Rule),
    MalformedRule(String, String),
}

enum LineError<I> {
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
        map(rule::parse, WellFormedRule),
    ))(StrTrace::new(i))
    .map_err(|e| match e {
        nom::Err::Error(e) => nom::Err::Error(LineError::CannotParse(i, format!("{}", e))),
        e => nom::Err::Error(LineError::CannotParse(i, format!("{:?}", e))),
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
    let lookup: Vec<(String, RuleDef)> = xs
        .iter()
        .map(|(source, l)| (source, parser(l)))
        .flat_map(|(source, r)| match r {
            Ok((t, rule)) if t.current.is_empty() => Some((source, rule)),
            Ok((_, _)) => None,
            Err(nom::Err::Error(LineError::CannotParse(i, why))) => {
                Some((source, MalformedRule(i.to_string(), why)))
            }
            Err(_) => None,
        })
        .map(|(source, line)| {
            let source = source.display().to_string();
            // todo;; support relative path parsing here
            let (_, file_name) = source.rsplit_once('/').expect("absolute path");
            (file_name.to_string(), line)
        })
        .map(|(source, line)| (source, line))
        .filter_map(|(source, line)| match line {
            WellFormedRule(r) => Some((source, RuleDef::ValidRule(r))),
            MalformedRule(text, error) => Some((source, RuleDef::Invalid { text, error })),
            SetDef(s) => Some((source, RuleDef::ValidSet(s))),
            _ => None,
        })
        .collect();

    Ok(lint_db(DB::from_sources(lookup)))
}

#[cfg(test)]
mod tests {
    use crate::read::deserialize_rules_db;
    use std::error::Error;

    #[test]
    fn deser_simple() -> Result<(), Box<dyn Error>> {
        let db = deserialize_rules_db(
            r#"
        [/foo.bar]
        allow perm=any all : all
        "#,
        )?;
        assert_eq!(db.len(), 1);
        assert_eq!(db.rules().len(), 1);
        assert!(db.rules().first().unwrap().valid);
        Ok(())
    }

    #[test]
    fn deser_set() -> Result<(), Box<dyn Error>> {
        let db = deserialize_rules_db(
            r#"
        [/foo.bar]
        %foo=bar
        allow perm=any all : all
        "#,
        )?;
        assert_eq!(db.len(), 2);
        assert_eq!(db.rules().len(), 1);
        assert_eq!(db.sets().len(), 1);
        Ok(())
    }

    #[test]
    fn deser_two_files() -> Result<(), Box<dyn Error>> {
        let db = deserialize_rules_db(
            r#"
        [/foo.rules]
        allow perm=execute all : all
        [/bar.rules]
        allow perm=any all : all
        "#,
        )?;
        assert_eq!(db.len(), 2);
        assert_eq!(db.rules().len(), 2);
        Ok(())
    }
}
