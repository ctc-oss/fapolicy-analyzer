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

use crate::dir_type::DirType;
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

pub(crate) fn dir_type(i: StrTrace) -> TraceResult<DirType> {
    match is_not(" \t\n")(i) {
        Ok((r, v)) if v.current == "execdirs" => Ok((r, DirType::ExecDirs)),
        Ok((r, v)) if v.current == "systemdirs" => Ok((r, DirType::SystemDirs)),
        Ok((r, v)) if v.current == "untrusted" => Ok((r, DirType::Untrusted)),
        Ok((r, v)) if v.current.starts_with('/') => Ok((r, DirType::Path(v.current.to_string()))),
        Ok((_, _)) => Err(nom::Err::Error(ExpectedDirPath(i))),
        Err(e) => Err(e),
    }
}

// todo;; this should be mimetype
pub(crate) fn filetype(i: StrTrace) -> TraceResult<Rvalue> {
    nom::bytes::complete::is_not(" \t\n")(i)
        .map(|(r, v)| (r, Rvalue::Literal(v.current.to_string())))
}

pub(crate) fn pattern(i: StrTrace) -> IResult<StrTrace, StrTrace, TraceError> {
    nom::bytes::complete::take_while1(|x| is_alphanumeric(x as u8) || x == '_')(i)
}

pub(crate) fn trust_flag(i: StrTrace) -> TraceResult<bool> {
    match digit1(i) {
        Ok((r, v)) if v.current == "1" => Ok((r, true)),
        Ok((r, v)) if v.current == "0" => Ok((r, false)),
        Ok((_, _)) => Err(nom::Err::Failure(Nom(i, ErrorKind::Digit))),
        Err(e) => Err(e),
    }
}

pub(crate) fn subject_object_parts(i: StrTrace) -> TraceResult<SubObj> {
    if !i.current.contains(':') {
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
        Ok((rem, v)) if v.current.is_empty() => Ok((rem, ())),
        Ok((_, v)) => Err(nom::Err::Error(ExpectedEndOfInput(v))),
        res => res.map(|(rem, _)| (rem, ())),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::dir_type::DirType;
    use assert_matches::assert_matches;

    #[test]
    fn parse_trust_flag() {
        assert!(trust_flag("1".into()).ok().unwrap().1);
        assert!(!trust_flag("0".into()).ok().unwrap().1);
        assert_eq!(None, trust_flag("2".into()).ok());
        assert_eq!(None, trust_flag("foo".into()).ok());
    }

    #[test]
    fn parse_dir_flag() {
        assert_eq!(
            dir_type("systemdirs".into()).unwrap().1,
            DirType::SystemDirs
        );
        assert_eq!(dir_type("execdirs".into()).unwrap().1, DirType::ExecDirs);
        assert_eq!(dir_type("untrusted".into()).unwrap().1, DirType::Untrusted);
        assert_eq!(
            dir_type("/mydir/".into()).unwrap().1,
            DirType::Path("/mydir/".to_string())
        );

        assert_matches!(
            dir_type("reldir/".into()),
            Err(nom::Err::Error(ExpectedDirPath(_)))
        );

        assert_matches!(
            dir_type("./reldir/".into()),
            Err(nom::Err::Error(ExpectedDirPath(_)))
        );
    }
}
