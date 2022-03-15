use nom::branch::alt;
use nom::bytes::complete::{tag, take_until};
use nom::combinator::{map, opt};
use nom::sequence::{separated_pair, tuple, Tuple};
use nom::{Err, IResult};

use crate::parser::error::RuleParseError;
use crate::parser::error::RuleParseError::*;
use crate::parser::trace::Trace;
use crate::{Decision, ObjPart, Object, Permission, Rvalue, SubjPart, Subject};
use nom::character::complete::{alphanumeric1, digit1, space0, space1};
use nom::character::is_alphanumeric;
use nom::error::ErrorKind;
use nom::multi::separated_list1;

type StrTrace<'a> = Trace<&'a str>;
type TraceError<'a> = RuleParseError<StrTrace<'a>>;
type NomTraceError<'a> = nom::error::Error<StrTrace<'a>>;
type TraceResult<'a, O> = IResult<StrTrace<'a>, O, TraceError<'a>>;

pub fn decision(i: StrTrace) -> TraceResult<Decision> {
    let (ii, r) = take_until(" ")(i)
        .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedDecision(i)))?;
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
        Ok((r, Some(dec))) => Ok((ii, dec)),
        Ok((r, None)) => Err(nom::Err::Error(UnknownDecision(i, r))),
        Err(e) => Err(nom::Err::Error(ExpectedDecision(i))),
    }
}

pub fn permission(i: StrTrace) -> TraceResult<Permission> {
    // checking the structure of the lhs without deriving any value
    let (ii, _) = match tuple((alphanumeric1, opt(tag("="))))(i) {
        Ok((r, (k, eq))) if k.fragment == "perm" => {
            if eq.is_some() {
                Ok((r, ()))
            } else {
                Err(nom::Err::Error(ExpectedPermAssignment(r)))
            }
        }
        Ok((r, (k, _))) => Err(nom::Err::Error(ExpectedPermTag(i, k))),
        Err(e) => Err(e),
    }?;

    let (remaining, r) = take_until(" ")(ii)?;
    let res: TraceResult<Option<Permission>> = opt(alt((
        map(tag("any"), |_| Permission::Any),
        map(tag("open"), |_| Permission::Open),
        map(tag("execute"), |_| Permission::Execute),
    )))(r);

    match res {
        Ok((_, Some(p))) => Ok((remaining, p)),
        Ok((r, None)) => Err(nom::Err::Error(ExpectedPermType(ii, r))),
        _ => Err(nom::Err::Error(ExpectedPermType(ii, r))),
    }
}

#[derive(Debug)]
pub struct SubObj {
    pub subject: Subject,
    pub object: Object,
}

fn filepath(i: StrTrace) -> TraceResult<StrTrace> {
    nom::bytes::complete::is_not(" \t\n")(i)
}

fn pattern(i: StrTrace) -> IResult<StrTrace, StrTrace, TraceError> {
    nom::bytes::complete::take_while1(|x| is_alphanumeric(x as u8) || x == '_')(i)
}

fn trust_flag(i: StrTrace) -> TraceResult<bool> {
    match digit1(i) {
        Ok((r, v)) if v.fragment == "1" => Ok((r, true)),
        Ok((r, v)) if v.fragment == "0" => Ok((r, false)),
        Ok((_, v)) => Err(nom::Err::Failure(Nom(i, ErrorKind::Digit))),
        Err(e) => Err(e),
    }
}

fn subj_part_uid(i: StrTrace) -> TraceResult<SubjPart> {
    match separated_pair(tag("uid"), tag("="), digit1)(i) {
        Ok((rem, (_, uid))) => Ok((rem, SubjPart::Uid(uid.fragment.parse().unwrap()))),
        Err(e) => Err(nom::Err::Error(SubjectPartExpectedInt(i))),
    }
}

fn subj_part(i: StrTrace) -> TraceResult<SubjPart> {
    match alt((
        map(tag("all"), |_| SubjPart::All),
        subj_part_uid,
        map(
            separated_pair(tag("gid"), tag("="), digit1),
            |x: (StrTrace, StrTrace)| SubjPart::Gid(x.1.fragment.parse().unwrap()),
        ),
        map(
            separated_pair(tag("exe"), tag("="), filepath),
            |x: (StrTrace, StrTrace)| SubjPart::Exe(x.1.fragment.to_string()),
        ),
        map(
            separated_pair(tag("pattern"), tag("="), pattern),
            |x: (StrTrace, StrTrace)| SubjPart::Pattern(x.1.fragment.to_string()),
        ),
        map(
            separated_pair(tag("comm"), tag("="), filepath),
            |x: (StrTrace, StrTrace)| SubjPart::Comm(x.1.fragment.to_string()),
        ),
        map(
            separated_pair(tag("trust"), tag("="), trust_flag),
            |x: (StrTrace, bool)| SubjPart::Trust(x.1),
        ),
    ))(i)
    {
        res => {
            println!("{:?}", res);
            res
        }
    }
}

pub fn subject(i: StrTrace) -> TraceResult<Subject> {
    let (ii, v) = take_until(":")(i)?;

    map(separated_list1(space1, subj_part), |parts| {
        Subject::new(parts)
    })(v)
    .map(|(_, v)| (ii, v))
}

fn obj_part(i: StrTrace) -> TraceResult<ObjPart> {
    alt((
        map(tag("all"), |_| ObjPart::All),
        map(
            separated_pair(tag("device"), tag("="), filepath),
            |x: (StrTrace, StrTrace)| ObjPart::Device(x.1.fragment.to_string()),
        ),
        map(
            separated_pair(tag("dir"), tag("="), filepath),
            |x: (StrTrace, StrTrace)| ObjPart::Dir(x.1.fragment.to_string()),
        ),
        map(
            separated_pair(tag("ftype"), tag("="), filepath),
            |x: (StrTrace, StrTrace)| ObjPart::FileType(Rvalue::Literal(x.1.fragment.to_string())),
        ),
        map(
            separated_pair(tag("path"), tag("="), filepath),
            |x: (StrTrace, StrTrace)| ObjPart::Path(x.1.fragment.to_string()),
        ),
        map(
            separated_pair(tag("trust"), tag("="), trust_flag),
            |x: (StrTrace, bool)| ObjPart::Trust(x.1),
        ),
    ))(i)
}

pub fn object(i: StrTrace) -> TraceResult<Object> {
    map(separated_list1(space1, obj_part), |parts| {
        Object::new(parts)
    })(i)
}

pub fn subject_object_parts(i: StrTrace) -> TraceResult<SubObj> {
    if !i.fragment.contains(":") {
        return Err(nom::Err::Error(MissingSeparator(i)));
    }

    match separated_pair(opt(subject), tuple((space0, tag(":"), space0)), opt(object))(i) {
        Ok((_, (None, None))) => Err(nom::Err::Error(MissingBothSubjObj(i))),
        Ok((_, (Some(_), None))) => Err(nom::Err::Error(MissingObject(i))),
        Ok((_, (None, Some(_)))) => Err(nom::Err::Error(MissingSubject(i))),
        Ok((remaining, (Some(s), Some(o)))) => Ok((
            remaining,
            SubObj {
                subject: s,
                object: o,
            },
        )),
        Err(e) => Err(e),
    }
}
