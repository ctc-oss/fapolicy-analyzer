/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fs::File;
use std::io::{BufRead, BufReader};

use nom::branch::alt;
use nom::combinator::map;

use crate::db::{RuleDef, DB};
use crate::error::Error;
use crate::read::Line::*;
use crate::{parse, Rule, Set};
use nom::error::{ErrorKind, ParseError};

enum Line {
    Comment(String),
    SetDef(Set),
    WellFormedRule(Rule),
    MalformedRule(String),
}

enum LineError<I> {
    CannotParse(I),
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

fn parser(i: &str) -> nom::IResult<&str, Line, LineError<&str>> {
    alt((
        map(parse::comment, Comment),
        map(parse::set, SetDef),
        map(parse::rule, WellFormedRule),
    ))(i)
    .map_err(|_| nom::Err::Error(LineError::CannotParse(i)))
}

pub fn load_rules_db(path: &str) -> Result<DB, Error> {
    let f = File::open(path)?;
    let buff = BufReader::new(f);

    let xs: Vec<String> = buff
        .lines()
        .map(|r| r.unwrap())
        .filter(|s| !s.is_empty() && !s.starts_with('#'))
        .collect();

    let lookup: Vec<RuleDef> = xs
        .iter()
        .map(|l| (l, parser(l)))
        .flat_map(|(_, r)| match r {
            Ok(("", rule)) => Some(rule),
            Ok((_, _)) => None,
            Err(nom::Err::Error(LineError::CannotParse(i))) => Some(MalformedRule(i.to_string())),
            Err(_) => None,
        })
        .filter_map(|line| match line {
            WellFormedRule(r) => Some(RuleDef::Valid(r)),
            MalformedRule(txt) => Some(RuleDef::Invalid(txt)),
            _ => None,
        })
        .collect();

    Ok(lookup.into())
}
