/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use nom::bytes::complete::{is_not, tag, take_until};

use nom::character::complete::digit1;
use nom::character::complete::space0;
use nom::character::is_alphanumeric;
use nom::combinator::rest;
use nom::error::ErrorKind;

use nom::sequence::tuple;

use crate::parser::error::RuleParseError;
use crate::parser::error::RuleParseError::*;
use crate::parser::object;
use crate::parser::subject;
use crate::parser::trace::Trace;

use crate::{Object, Rvalue, Subject};
use nom::IResult;

// general parser defs and functions

pub type StrTrace<'a> = Trace<&'a str>;
pub(crate) type TraceError<'a> = RuleParseError<StrTrace<'a>>;
pub(crate) type NomTraceError<'a> = nom::error::Error<StrTrace<'a>>;
pub(crate) type TraceResult<'a, O> = IResult<StrTrace<'a>, O, TraceError<'a>>;

#[derive(Debug)]
pub(crate) struct SubObj {
    pub subject: Subject,
    pub object: Object,
}

// todo;; this should be absolute path
pub(crate) fn filepath(i: StrTrace) -> TraceResult<StrTrace> {
    nom::bytes::complete::is_not(" \t\n")(i)
}

// todo;; this should be mimetype
pub(crate) fn filetype(i: StrTrace) -> TraceResult<Rvalue> {
    nom::bytes::complete::is_not(" \t\n")(i)
        .map(|(r, v)| (r, Rvalue::Literal(v.fragment.to_string())))
}

pub(crate) fn pattern(i: StrTrace) -> IResult<StrTrace, StrTrace, TraceError> {
    nom::bytes::complete::take_while1(|x| is_alphanumeric(x as u8) || x == '_')(i)
}

pub(crate) fn trust_flag(i: StrTrace) -> TraceResult<bool> {
    match digit1(i) {
        Ok((r, v)) if v.fragment == "1" => Ok((r, true)),
        Ok((r, v)) if v.fragment == "0" => Ok((r, false)),
        Ok((_, _)) => Err(nom::Err::Failure(Nom(i, ErrorKind::Digit))),
        Err(e) => Err(e),
    }
}

pub(crate) fn subject_object_parts(i: StrTrace) -> TraceResult<SubObj> {
    if !i.fragment.contains(':') {
        return Err(nom::Err::Error(MissingSeparator(i)));
    }

    let (_, ss) = take_until(" :")(i)?;
    let (_, s) = subject::parse(ss)?;

    let (_, (_, _, _, oo)) = tuple((is_not(":"), tag(":"), space0, rest))(i)?;
    let (ii, o) = object::parse(oo)?;

    Ok((
        ii,
        SubObj {
            subject: s,
            object: o,
        },
    ))
}

pub(crate) fn end_of_rule(i: StrTrace) -> nom::IResult<StrTrace, (), RuleParseError<StrTrace>> {
    match rest(i) {
        Ok((rem, v)) if v.fragment.is_empty() => Ok((rem, ())),
        Ok((_, v)) => Err(nom::Err::Error(ExpectedEndOfInput(v))),
        res => res.map(|(rem, _)| (rem, ())),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_trust_flag() {
        assert!(trust_flag("1".into()).ok().unwrap().1);
        assert!(!trust_flag("0".into()).ok().unwrap().1);
        assert_eq!(None, trust_flag("2".into()).ok());
        assert_eq!(None, trust_flag("foo".into()).ok());
    }
}
