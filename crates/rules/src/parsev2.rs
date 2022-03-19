use nom::branch::alt;
use nom::bytes::complete::{is_not, tag, take_till, take_until};
use nom::combinator::{eof, map, opt, rest};
use nom::sequence::{delimited, separated_pair, terminated, tuple, Tuple};
use nom::{Err, IResult, Parser};

use crate::parser::error::RuleParseError;
use crate::parser::error::RuleParseError::*;
use crate::parser::trace::Trace;
use crate::{Decision, ObjPart, Object, Permission, Rvalue, SubjPart, Subject};
use nom::character::complete::{
    alpha1, alphanumeric1, digit1, multispace0, not_line_ending, one_of, space0, space1,
};
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

// todo;; this should be absolute path
fn filepath(i: StrTrace) -> TraceResult<StrTrace> {
    nom::bytes::complete::is_not(" \t\n")(i)
}

// todo;; this should be mimetype
fn filetype(i: StrTrace) -> TraceResult<Rvalue> {
    nom::bytes::complete::is_not(" \t\n")(i)
        .map(|(r, v)| (r, Rvalue::Literal(v.fragment.to_string())))
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
    let (ii, _) = tag("uid")(i)?;
    let (ii, _) = tag("=")(ii)?;
    let (ii, uid) =
        digit1(ii).map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedInt(ii)))?;

    Ok((ii, SubjPart::Uid(uid.fragment.parse().unwrap())))
}

fn subj_part(i: StrTrace) -> TraceResult<SubjPart> {
    let (ii, x) = alt((tag("all"), terminated(alpha1, tag("="))))(i)
        .map_err(|e: nom::Err<TraceError>| nom::Err::Error(SubjectPartExpected(i)))?;

    match x.fragment {
        "all" => Ok((ii, SubjPart::All)),

        "uid" => digit1(ii)
            .map(|(ii, d)| (ii, SubjPart::Uid(d.fragment.parse().unwrap())))
            .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedInt(i))),

        "gid" => digit1(ii)
            .map(|(ii, d)| (ii, SubjPart::Gid(d.fragment.parse().unwrap())))
            .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedInt(i))),

        "exe" => filepath(ii)
            .map(|(ii, d)| (ii, SubjPart::Exe(d.fragment.to_string())))
            .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedFilePath(i))),

        "pattern" => pattern(ii)
            .map(|(ii, d)| (ii, SubjPart::Pattern(d.fragment.to_string())))
            .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedPattern(i))),

        "comm" => filepath(ii)
            .map(|(ii, d)| (ii, SubjPart::Comm(d.fragment.to_string())))
            .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedFilePath(i))),

        "trust" => trust_flag(ii)
            .map(|(ii, d)| (ii, SubjPart::Trust(d)))
            .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedBoolean(i))),

        _ => Err(nom::Err::Error(UnknownSubjectPart(i))),
    }
}

// allow perm=any uid=1 : all
pub fn subject(i: StrTrace) -> TraceResult<Subject> {
    let (_, mut ii) = take_until(" :")(i)?;

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

    // match map(wrapped_parser, |parts| {
    //     Subject::new(parts.into_iter().map(|(a, _)| a).collect())
    // })(ii)
    // .map_err(|e: nom::Err<TraceError>| nom::Err::Error(SubjectPartExpectedInt(i)))
    // {
    //     Ok((ii, r)) if ii.fragment.is_empty() => Ok((ii, r)),
    //     Ok((ii, r)) => subj_part(ii)
    //         .map(|_| (i, Subject::empty()))
    //         .map_err(|e| nom::error::Error()),
    //     res => res,
    // }
}

pub fn object(i: StrTrace) -> TraceResult<Object> {
    let (_, (_, _, _, mut ii)) = tuple((is_not(":"), tag(":"), space0, rest))(i)?;

    let mut parts = vec![];
    loop {
        if ii.fragment.trim().is_empty() {
            break;
        }

        let (i, part) = delimited(multispace0, obj_part, multispace0)(ii)?;
        ii = i;
        parts.push(part);
    }

    // todo;; check for 'all' here, if there are additional entries other than 'trust', its an error

    Ok((ii, Object::new(parts)))
}

fn obj_part(i: StrTrace) -> TraceResult<ObjPart> {
    let (ii, x) = alt((tag("all"), terminated(alpha1, tag("="))))(i)
        .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ObjectPartExpected(i)))?;

    match x.fragment {
        "all" => Ok((ii, ObjPart::All)),

        "device" => filepath(ii)
            .map(|(ii, d)| (ii, ObjPart::Device(d.fragment.to_string())))
            .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedFilePath(i))),

        "dir" => filepath(ii)
            .map(|(ii, d)| (ii, ObjPart::Dir(d.fragment.to_string())))
            .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedDirPath(i))),

        "ftype" => filetype(ii)
            .map(|(ii, d)| (ii, ObjPart::FileType(d)))
            .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedFileType(i))),

        "path" => filepath(ii)
            .map(|(ii, d)| (ii, ObjPart::Path(d.fragment.to_string())))
            .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedFilePath(i))),

        "trust" => trust_flag(ii)
            .map(|(ii, d)| (ii, ObjPart::Trust(d)))
            .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedBoolean(i))),

        _ => Err(nom::Err::Error(UnknownObjectPart(i))),
    }

    //     alt((
    //     map(tag("all"), |_| ObjPart::All),
    //     map(
    //         separated_pair(tag("device"), tag("="), filepath),
    //         |x: (StrTrace, StrTrace)| ObjPart::Device(x.1.fragment.to_string()),
    //     ),
    //     map(
    //         separated_pair(tag("dir"), tag("="), filepath),
    //         |x: (StrTrace, StrTrace)| ObjPart::Dir(x.1.fragment.to_string()),
    //     ),
    //     map(
    //         separated_pair(tag("ftype"), tag("="), filepath),
    //         |x: (StrTrace, StrTrace)| ObjPart::FileType(Rvalue::Literal(x.1.fragment.to_string())),
    //     ),
    //     map(
    //         separated_pair(tag("path"), tag("="), filepath),
    //         |x: (StrTrace, StrTrace)| ObjPart::Path(x.1.fragment.to_string()),
    //     ),
    //     map(
    //         separated_pair(tag("trust"), tag("="), trust_flag),
    //         |x: (StrTrace, bool)| ObjPart::Trust(x.1),
    //     ),
    // ))(i)
}

pub fn subject_object_parts(i: StrTrace) -> TraceResult<SubObj> {
    if !i.fragment.contains(":") {
        return Err(nom::Err::Error(MissingSeparator(i)));
    }

    // pass the same input to both the subject and object parsers
    // inside the subject parser take until the :
    // inside the object parser take after the :
    //
    // doing this should allow each of them to locate errors without the other one interfering

    let (_, s) = subject(i)?;
    let (ii, o) = object(i)?;

    Ok((
        ii,
        SubObj {
            subject: s,
            object: o,
        },
    ))

    // match separated_pair(subject, tuple((space0, tag(":"), space0)), object)(i) {
    //     // Ok((_, (None, None))) => Err(nom::Err::Error(MissingBothSubjObj(i))),
    //     // Ok((_, (Some(_), None))) => Err(nom::Err::Error(MissingObject(i))),
    //     // Ok((_, (None, Some(_)))) => Err(nom::Err::Error(MissingSubject(i))),
    //     Ok((remaining, (s, o))) => Ok((
    //         remaining,
    //         SubObj {
    //             subject: s,
    //             object: o,
    //         },
    //     )),
    //     Err(e) => Err(e),
    // }
}
