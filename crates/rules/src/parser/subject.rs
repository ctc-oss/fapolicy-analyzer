/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use nom::branch::alt;
use nom::bytes::complete::tag;

use nom::character::complete::digit1;
use nom::character::complete::{alpha1, multispace0};

use nom::sequence::{delimited, terminated};

use crate::parser::error::RuleParseError::*;

use crate::subject::Part as SubjPart;
use crate::Subject;

use crate::parser::parse::{filepath, pattern, trust_flag, StrTrace, TraceError, TraceResult};

fn subj_part(i: StrTrace) -> TraceResult<SubjPart> {
    let (ii, x) = alt((tag("all"), terminated(alpha1, tag("="))))(i)
        .map_err(|_: nom::Err<TraceError>| nom::Err::Error(SubjectPartExpected(i)))?;

    match x.current {
        "all" => Ok((ii, SubjPart::All)),

        "uid" => digit1(ii)
            .map(|(ii, d)| (ii, SubjPart::Uid(d.current.parse().unwrap())))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedInt(i))),

        "gid" => digit1(ii)
            .map(|(ii, d)| (ii, SubjPart::Gid(d.current.parse().unwrap())))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedInt(i))),

        "pid" => digit1(ii)
            .map(|(ii, d)| (ii, SubjPart::Pid(d.current.parse().unwrap())))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedInt(i))),

        "exe" => filepath(ii)
            .map(|(ii, d)| (ii, SubjPart::Exe(d.current.to_string())))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedFilePath(i))),

        "pattern" => pattern(ii)
            .map(|(ii, d)| (ii, SubjPart::Pattern(d.current.to_string())))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedPattern(i))),

        "comm" => filepath(ii)
            .map(|(ii, d)| (ii, SubjPart::Comm(d.current.to_string())))
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
        if ii.current.trim().is_empty() {
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
