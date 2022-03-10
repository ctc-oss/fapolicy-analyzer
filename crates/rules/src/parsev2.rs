use crate::parser::trace::Trace;
use crate::Decision;
use nom::branch::alt;
use nom::bytes::complete::tag;
use nom::combinator::map;

type StrTrace<'a> = Trace<&'a str>;

pub fn decision(i: StrTrace) -> nom::IResult<StrTrace, Decision> {
    alt((
        map(tag("allow_audit"), |_| Decision::AllowAudit),
        map(tag("allow_syslog"), |_| Decision::AllowSyslog),
        map(tag("allow_log"), |_| Decision::AllowLog),
        map(tag("allow"), |_| Decision::Allow),
        map(tag("deny_audit"), |_| Decision::DenyAudit),
        map(tag("deny_syslog"), |_| Decision::DenySyslog),
        map(tag("deny_log"), |_| Decision::DenyLog),
        map(tag("deny"), |_| Decision::Deny),
    ))(i)
}
