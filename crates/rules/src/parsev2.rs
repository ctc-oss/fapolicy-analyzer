use nom::branch::alt;
use nom::bytes::complete::tag;
use nom::character::complete::alphanumeric1;
use nom::combinator::{map, opt};
use nom::sequence::tuple;
use nom::IResult;

use crate::parser::error::RuleParseError;
use crate::parser::error::RuleParseError::*;
use crate::parser::trace::Trace;
use crate::{Decision, Permission};

type StrTrace<'a> = Trace<&'a str>;
type TraceError<'a> = RuleParseError<StrTrace<'a>>;
type NomTraceError<'a> = nom::error::Error<StrTrace<'a>>;

pub fn decision(i: StrTrace) -> IResult<StrTrace, Decision, TraceError> {
    let x: IResult<StrTrace, Decision, NomTraceError> = alt((
        map(tag("allow_audit"), |_| Decision::AllowAudit),
        map(tag("allow_syslog"), |_| Decision::AllowSyslog),
        map(tag("allow_log"), |_| Decision::AllowLog),
        map(tag("allow"), |_| Decision::Allow),
        map(tag("deny_audit"), |_| Decision::DenyAudit),
        map(tag("deny_syslog"), |_| Decision::DenySyslog),
        map(tag("deny_log"), |_| Decision::DenyLog),
        map(tag("deny"), |_| Decision::Deny),
    ))(i);

    match x {
        Ok((r, dec)) => Ok((r, dec)),
        Err(e) => {
            let guessed = i
                .fragment
                .split_once(" ")
                .map(|x| UnknownDecision(i) /*(x.0, i.len())*/)
                .unwrap_or_else(
                    || ExpectedDecision(i), /*(
                                                i.clone().split_once(" ").map(|x| x.0).unwrap_or_else(|| i),
                                                i.len(),
                                            )*/
                );
            Err(nom::Err::Error(guessed))
        }
    }
}

pub fn permission(i: StrTrace) -> IResult<StrTrace, Permission, TraceError> {
    // checking the structure of the lhs without deriving any value
    let (ii, _) = match tuple((alphanumeric1, opt(tag("="))))(i) {
        Ok((r, (k, eq))) if k.fragment == "perm" => {
            if eq.is_some() {
                Ok((r, ()))
            } else {
                Err(nom::Err::Error(
                    ExpectedPermAssignment(r), /*(k, i.len() - 4)*/
                ))
            }
        }
        Ok((r, (k, _))) => Err(nom::Err::Error(ExpectedPermTag(r) /*(k, i.len())*/)),
        Err(e) => Err(e),
    }?;

    // continue the parsing with the remainder from the check above (ii)
    let res: IResult<StrTrace, Option<Permission>, TraceError> = opt(alt((
        map(tag("any"), |_| Permission::Any),
        map(tag("open"), |_| Permission::Open),
        map(tag("execute"), |_| Permission::Execute),
    )))(ii);

    match res {
        Ok((r, Some(p))) => Ok((r, p)),
        Ok((r, None)) => Err(nom::Err::Error(ExpectedPermType(r) /*(i, i.len())*/)),
        _ => Err(nom::Err::Error(ExpectedPermType(i) /*(i, i.len())*/)),
    }
}
