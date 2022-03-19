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

pub type StrTrace<'a> = Trace<&'a str>;
pub(crate) type TraceError<'a> = RuleParseError<StrTrace<'a>>;
pub(crate) type NomTraceError<'a> = nom::error::Error<StrTrace<'a>>;
pub(crate) type TraceResult<'a, O> = IResult<StrTrace<'a>, O, TraceError<'a>>;

pub(crate) fn decision(i: StrTrace) -> TraceResult<Decision> {
    // let (ii, r) = take_until(" ")(i)
    //     .map_err(|e: nom::Err<TraceError>| nom::Err::Error(ExpectedDecision(i)))?;

    let (ii, r) = recognize(pair(
        alt((alpha1, tag("_"))),
        many0_count(alt((alphanumeric1, tag("_")))),
    ))(i)
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

pub(crate) fn permission(i: StrTrace) -> TraceResult<Permission> {
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

    // let (remaining, r) = take_until(" ")(ii)?;
    let (remaining, r) = alpha1(ii)?;
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
struct SubObj {
    pub subject: Subject,
    pub object: Object,
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

        "pid" => digit1(ii)
            .map(|(ii, d)| (ii, SubjPart::Pid(d.fragment.parse().unwrap())))
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

pub(crate) fn subject(i: StrTrace) -> TraceResult<Subject> {
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
}

pub(crate) fn object(i: StrTrace) -> TraceResult<Object> {
    let mut ii = i;
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

fn subject_object_parts(i: StrTrace) -> TraceResult<SubObj> {
    if !i.fragment.contains(":") {
        return Err(nom::Err::Error(MissingSeparator(i)));
    }

    let (_, ss) = take_until(" :")(i)?;
    let (_, s) = subject(ss)?;

    let (_, (_, _, _, oo)) = tuple((is_not(":"), tag(":"), space0, rest))(i)?;
    let (ii, o) = object(oo)?;

    Ok((
        ii,
        SubObj {
            subject: s,
            object: o,
        },
    ))
}

fn end_of_rule(i: StrTrace) -> nom::IResult<StrTrace, (), RuleParseError<StrTrace>> {
    match rest(i) {
        Ok((rem, v)) if v.fragment.is_empty() => Ok((rem, ())),
        Ok((rem, v)) => Err(nom::Err::Error(ExpectedEndOfInput(v))),
        res => res.map(|(rem, _)| (rem, ())),
    }
}

pub fn rule(i: StrTrace) -> TraceResult<Rule> {
    match nom::combinator::complete(nom::sequence::tuple((
        terminated(decision, space1),
        terminated(permission, space0),
        subject_object_parts,
        end_of_rule,
    )))(i)
    {
        Ok((remaining_input, (dec, perm, so, _))) => Ok((
            remaining_input,
            Rule {
                subj: so.subject,
                perm,
                obj: so.object,
                dec,
            },
        )),
        Err(e) => Err(e),
        // Err(nom::Err::Error(e)) => ErrorAt::from(e).into(),
        // _ => panic!("hmmm what to do with this one..."),
    }
}

pub fn set(i: StrTrace) -> TraceResult<Set> {
    match nom::combinator::complete(nom::sequence::tuple((
        tag("%"),
        separated_pair(
            alphanumeric1,
            tag("="),
            separated_list1(tag(","), is_not(",")),
        ),
    )))(i)
    {
        Ok((remaining_input, (_, (var, def)))) => Ok((
            remaining_input,
            Set::new(
                var.fragment,
                def.iter().map(|s| s.fragment.to_string()).collect(),
            ),
        )),
        Err(e) => Err(e),
    }
}

pub fn comment(i: StrTrace) -> TraceResult<String> {
    match nom::combinator::complete(preceded(tag("#"), is_not("\n")))(i) {
        Ok((remaining, c)) => Ok((remaining, c.fragment.to_string())),
        Err(e) => Err(e),
    }
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

    #[test]
    fn parse_perm() {
        assert_eq!(
            Permission::Any,
            permission("perm=any".into()).ok().unwrap().1
        );
    }

    #[test]
    fn parse_obj_part() {
        assert_eq!(ObjPart::All, obj_part("all".into()).ok().unwrap().1);
    }

    #[test]
    fn parse_obj() {
        assert_eq!(
            Object::new(vec![ObjPart::All, ObjPart::Trust(true)]),
            object("all trust=1".into()).ok().unwrap().1
        );

        assert_eq!(
            Object::new(vec![ObjPart::Trust(true)]),
            object("trust=1".into()).ok().unwrap().1
        );

        // ordering matters
        assert_eq!(
            Object::new(vec![ObjPart::Trust(true), ObjPart::All]),
            object("trust=1 all".into()).ok().unwrap().1
        );
    }

    #[test]
    fn parse_dec() {
        assert_eq!(Decision::Allow, decision("allow".into()).ok().unwrap().1);
        assert_eq!(Decision::Deny, decision("deny".into()).ok().unwrap().1);
        assert_eq!(
            Decision::AllowLog,
            decision("allow_log".into()).ok().unwrap().1
        );
        assert_eq!(
            Decision::DenyLog,
            decision("deny_log".into()).ok().unwrap().1
        );
        assert_eq!(
            Decision::DenyAudit,
            decision("deny_audit".into()).ok().unwrap().1
        );
        assert_eq!(
            Decision::AllowAudit,
            decision("allow_audit".into()).ok().unwrap().1
        );
    }

    // todo;; need better error propagation, and then better negative tests
    #[test]
    fn bad_rules() {
        rule("deny_audit perm=open all : foo".into()).err().unwrap();
        rule("deny_audit perm=open all trust=foo : all".into())
            .err()
            .unwrap();

        rule("deny_audit perm=open all : all trust=1 foo".into())
            .err()
            .unwrap();

        rule("deny_audit perm=open all : all trust=foo".into())
            .err()
            .unwrap();
    }

    #[test]
    fn parse_rule() {
        let (rem, r) = rule("deny_audit perm=any pattern=ld_so : all".into())
            .ok()
            .unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Any, r.perm);
        assert_eq!(Subject::from(SubjPart::Pattern("ld_so".into())), r.subj);
        assert_eq!(Object::from(ObjPart::All), r.obj);
        assert!(rem.is_empty());

        let (rem, r) = rule("deny_audit perm=any all : all".into()).ok().unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Any, r.perm);
        assert_eq!(Subject::from(SubjPart::All), r.subj);
        assert_eq!(Object::from(ObjPart::All), r.obj);
        assert!(rem.is_empty());

        let (rem, r) = rule("deny_audit perm=open all : device=/dev/cdrom".into())
            .ok()
            .unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Open, r.perm);
        assert_eq!(Subject::from(SubjPart::All), r.subj);
        assert_eq!(Object::from(ObjPart::Device("/dev/cdrom".into())), r.obj);
        assert!(rem.is_empty());

        let (rem, r) = rule("deny_audit perm=open exe=/usr/bin/ssh : dir=/opt".into())
            .ok()
            .unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Open, r.perm);
        assert_eq!(Subject::from(SubjPart::Exe("/usr/bin/ssh".into())), r.subj);
        assert_eq!(Object::from(ObjPart::Dir("/opt".into())), r.obj);
        assert!(rem.is_empty());

        let (rem, r) = rule("deny_audit perm=any all : ftype=application/x-bad-elf".into())
            .ok()
            .unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Any, r.perm);
        assert_eq!(Subject::from(SubjPart::All), r.subj);
        assert_eq!(
            Object::from(ObjPart::FileType(Rvalue::Literal(
                "application/x-bad-elf".into()
            ))),
            r.obj
        );
        assert!(rem.is_empty());
    }

    #[test]
    fn parse_set() {
        let def = "%lang=application/x-bytecode.ocaml,application/x-bytecode.python,application/java-archive,text/x-java";
        let md = set(def.into()).ok().unwrap().1;

        assert_eq!("lang", md.name);
        assert_eq!(
            vec![
                "application/x-bytecode.ocaml",
                "application/x-bytecode.python",
                "application/java-archive",
                "text/x-java"
            ],
            md.values
        );
    }

    #[test]
    fn parse_trust_flag() {
        assert!(trust_flag("1".into()).ok().unwrap().1);
        assert!(!trust_flag("0".into()).ok().unwrap().1);
        assert_eq!(None, trust_flag("2".into()).ok());
        assert_eq!(None, trust_flag("foo".into()).ok());
    }
}
