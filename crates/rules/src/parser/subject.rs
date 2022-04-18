/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use nom::branch::alt;
use nom::bytes::complete::{is_not, tag, take_until};
use nom::character::complete::space1;
use nom::character::complete::{alpha1, multispace0, space0};
use nom::character::complete::{alphanumeric1, digit1};
use nom::character::is_alphanumeric;
use nom::combinator::{map, opt, recognize, rest};
use nom::error::ErrorKind;
use nom::multi::{many0_count, separated_list1};
use nom::sequence::{delimited, pair, preceded, separated_pair, terminated, tuple};

use crate::object::Part as ObjPart;
use crate::parser::error::RuleParseError;
use crate::parser::error::RuleParseError::*;
use crate::parser::trace::Trace;
use crate::set::Set;
use crate::subject::Part as SubjPart;
use crate::{Decision, Object, Permission, Rule, Rvalue, Subject};
use nom::IResult;

use crate::parser::parse::{
    filepath, pattern, trust_flag, NomTraceError, StrTrace, TraceError, TraceResult,
};

fn subj_part(i: StrTrace) -> TraceResult<SubjPart> {
    let (ii, x) = alt((tag("all"), terminated(alpha1, tag("="))))(i)
        .map_err(|_: nom::Err<TraceError>| nom::Err::Error(SubjectPartExpected(i)))?;

    match x.fragment {
        "all" => Ok((ii, SubjPart::All)),

        "uid" => digit1(ii)
            .map(|(ii, d)| (ii, SubjPart::Uid(d.fragment.parse().unwrap())))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedInt(i))),

        "gid" => digit1(ii)
            .map(|(ii, d)| (ii, SubjPart::Gid(d.fragment.parse().unwrap())))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedInt(i))),

        "pid" => digit1(ii)
            .map(|(ii, d)| (ii, SubjPart::Pid(d.fragment.parse().unwrap())))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedInt(i))),

        "exe" => filepath(ii)
            .map(|(ii, d)| (ii, SubjPart::Exe(d.fragment.to_string())))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedFilePath(i))),

        "pattern" => pattern(ii)
            .map(|(ii, d)| (ii, SubjPart::Pattern(d.fragment.to_string())))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedPattern(i))),

        "comm" => filepath(ii)
            .map(|(ii, d)| (ii, SubjPart::Comm(d.fragment.to_string())))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedFilePath(i))),

        "trust" => trust_flag(ii)
            .map(|(ii, d)| (ii, SubjPart::Trust(d)))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedBoolean(i))),

        _ => Err(nom::Err::Error(UnknownSubjectPart(i))),
    }
}

pub(crate) fn parse(i: StrTrace) -> TraceResult<Subject> {
    let mut ii = i;
    let mut parts = vec![];
    loop {
        if ii.fragment.trim().is_empty() {
            break;
        }

        let (i, part) = delimited(multispace0, subj_part, multispace0)(ii)?;
        ii = i;
        parts.push(part);
    }

    // todo;; check for 'all' here, if there are additional entries other than 'trust', its an error

    Ok((ii, Subject::new(parts)))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_subj_part() {
        assert_eq!(SubjPart::All, subj_part("all".into()).ok().unwrap().1);
        assert_eq!(
            SubjPart::Uid(10001),
            subj_part("uid=10001".into()).ok().unwrap().1
        );
        assert_eq!(SubjPart::Gid(0), subj_part("gid=0".into()).ok().unwrap().1);
    }
}
