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

use crate::parser::parse::{NomTraceError, StrTrace, TraceError, TraceResult};

pub(crate) fn parse(i: StrTrace) -> TraceResult<Decision> {
    // let (ii, r) = take_until(" ")(i)
    //     .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedDecision(i)))?;

    let (ii, r) = recognize(pair(
        alt((alpha1, tag("_"))),
        many0_count(alt((alphanumeric1, tag("_")))),
    ))(i)
    .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedDecision(i)))?;

    let x: IResult<StrTrace, Option<Decision>, NomTraceError> = opt(alt((
        map(tag("allow_audit"), |_| Decision::AllowAudit),
        map(tag("allow_syslog"), |_| Decision::AllowSyslog),
        map(tag("allow_log"), |_| Decision::AllowLog),
        map(tag("allow"), |_| Decision::Allow),
        map(tag("deny_audit"), |_| Decision::DenyAudit),
        map(tag("deny_syslog"), |_| Decision::DenySyslog),
        map(tag("deny_log"), |_| Decision::DenyLog),
        map(tag("deny"), |_| Decision::Deny),
    )))(r);

    match x {
        Ok((_, Some(dec))) => Ok((ii, dec)),
        Ok((r, None)) => Err(nom::Err::Error(UnknownDecision(i, r))),
        Err(_) => Err(nom::Err::Error(ExpectedDecision(i))),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_dec() {
        assert_eq!(Decision::Allow, parse("allow".into()).ok().unwrap().1);
        assert_eq!(Decision::Deny, parse("deny".into()).ok().unwrap().1);
        assert_eq!(
            Decision::AllowLog,
            parse("allow_log".into()).ok().unwrap().1
        );
        assert_eq!(Decision::DenyLog, parse("deny_log".into()).ok().unwrap().1);
        assert_eq!(
            Decision::DenyAudit,
            parse("deny_audit".into()).ok().unwrap().1
        );
        assert_eq!(
            Decision::AllowAudit,
            parse("allow_audit".into()).ok().unwrap().1
        );
    }
}
