use nom::branch::alt;
use nom::bytes::complete::{is_not, tag};
use nom::character::complete::space0;
use nom::character::complete::space1;
use nom::character::complete::{alphanumeric1, digit1};
use nom::character::is_alphanumeric;
use nom::combinator::map;
use nom::error::{Error, ErrorKind};
use nom::multi::separated_list1;
use nom::sequence::{preceded, separated_pair, terminated};

use crate::rules::file_type::Rvalue::Literal;
use crate::rules::object::Part as ObjPart;
use crate::rules::set::Set;
use crate::rules::subject::Part as SubjPart;
use crate::rules::{Decision, Object, Permission, Rule, Subject};

pub(crate) fn decision(i: &str) -> nom::IResult<&str, Decision> {
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

pub(crate) fn permission(i: &str) -> nom::IResult<&str, Permission> {
    alt((
        map(separated_pair(tag("perm"), tag("="), tag("any")), |_| {
            Permission::Any
        }),
        map(separated_pair(tag("perm"), tag("="), tag("open")), |_| {
            Permission::Open
        }),
        map(
            separated_pair(tag("perm"), tag("="), tag("execute")),
            |_| Permission::Execute,
        ),
    ))(i)
}

fn subj_part(i: &str) -> nom::IResult<&str, SubjPart> {
    alt((
        map(tag("all"), |_| SubjPart::All),
        map(
            separated_pair(tag("uid"), tag("="), digit1),
            |x: (&str, &str)| SubjPart::Uid(x.1.parse().unwrap()),
        ),
        map(
            separated_pair(tag("gid"), tag("="), digit1),
            |x: (&str, &str)| SubjPart::Gid(x.1.parse().unwrap()),
        ),
        map(
            separated_pair(tag("exe"), tag("="), filepath),
            |x: (&str, &str)| SubjPart::Exe(x.1.to_string()),
        ),
        map(
            separated_pair(tag("pattern"), tag("="), pattern),
            |x: (&str, &str)| SubjPart::Pattern(x.1.to_string()),
        ),
        map(
            separated_pair(tag("comm"), tag("="), filepath),
            |x: (&str, &str)| SubjPart::Comm(x.1.to_string()),
        ),
        map(
            separated_pair(tag("trust"), tag("="), trust_flag),
            |x: (&str, bool)| SubjPart::Trust(x.1),
        ),
    ))(i)
}

pub(crate) fn subject(i: &str) -> nom::IResult<&str, Subject> {
    map(separated_list1(space1, subj_part), |parts| {
        Subject::new(parts)
    })(i)
}

fn obj_part(i: &str) -> nom::IResult<&str, ObjPart> {
    alt((
        map(tag("all"), |_| ObjPart::All),
        map(
            separated_pair(tag("device"), tag("="), filepath),
            |x: (&str, &str)| ObjPart::Device(x.1.to_string()),
        ),
        map(
            separated_pair(tag("dir"), tag("="), filepath),
            |x: (&str, &str)| ObjPart::Dir(x.1.to_string()),
        ),
        map(
            separated_pair(tag("ftype"), tag("="), filepath),
            |x: (&str, &str)| ObjPart::FileType(Literal(x.1.to_string())),
        ),
        map(
            separated_pair(tag("path"), tag("="), filepath),
            |x: (&str, &str)| ObjPart::Path(x.1.to_string()),
        ),
        map(
            separated_pair(tag("trust"), tag("="), trust_flag),
            |x: (&str, bool)| ObjPart::Trust(x.1),
        ),
    ))(i)
}

pub(crate) fn object(i: &str) -> nom::IResult<&str, Object> {
    map(separated_list1(space1, obj_part), |parts| {
        Object::new(parts)
    })(i)
}

fn filepath(i: &str) -> nom::IResult<&str, &str> {
    nom::bytes::complete::is_not(" \t\n")(i)
}

fn pattern(i: &str) -> nom::IResult<&str, &str> {
    nom::bytes::complete::take_while1(|x| is_alphanumeric(x as u8) || x == '_')(i)
}

fn trust_flag(i: &str) -> nom::IResult<&str, bool> {
    match digit1(i) {
        Ok((r, "1")) => Ok((r, true)),
        Ok((r, "0")) => Ok((r, false)),
        Ok((_, v)) => Err(nom::Err::Failure(Error {
            input: v,
            code: ErrorKind::Digit,
        })),
        Err(e) => Err(e),
    }
}

pub fn rule(i: &str) -> nom::IResult<&str, Rule> {
    match nom::combinator::complete(nom::sequence::tuple((
        terminated(decision, space1),
        terminated(permission, space1),
        terminated(subject, space0),
        terminated(tag(":"), space0),
        object,
    )))(i)
    {
        Ok((remaining_input, (dec, perm, subj, _, obj))) => {
            Ok((remaining_input, Rule::new(subj, perm, obj, dec)))
        }
        Err(e) => Err(e),
    }
}

pub fn set(i: &str) -> nom::IResult<&str, Set> {
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
            Set::new(var, def.iter().map(|&s| s.into()).collect()),
        )),
        Err(e) => Err(e),
    }
}

pub fn comment(i: &str) -> nom::IResult<&str, String> {
    match nom::combinator::complete(preceded(tag("#"), is_not("\n")))(i) {
        Ok((remaining, c)) => Ok((remaining, c.into())),
        Err(e) => Err(e),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_subj_part() {
        assert_eq!(SubjPart::All, subj_part("all").ok().unwrap().1);
        assert_eq!(SubjPart::Uid(10001), subj_part("uid=10001").ok().unwrap().1);
        assert_eq!(SubjPart::Gid(0), subj_part("gid=0").ok().unwrap().1);
    }

    #[test]
    fn parse_perm() {
        assert_eq!(Permission::Any, permission("perm=any").ok().unwrap().1);
    }

    #[test]
    fn parse_obj_part() {
        assert_eq!(ObjPart::All, obj_part("all").ok().unwrap().1);
    }

    #[test]
    fn parse_obj() {
        assert_eq!(
            Object::new(vec![ObjPart::All, ObjPart::Trust(true)]),
            object("all trust=1").ok().unwrap().1
        );

        assert_eq!(
            Object::new(vec![ObjPart::Trust(true)]),
            object("trust=1").ok().unwrap().1
        );

        // ordering matters
        assert_eq!(
            Object::new(vec![ObjPart::Trust(true), ObjPart::All]),
            object("trust=1 all").ok().unwrap().1
        );
    }

    #[test]
    fn parse_dec() {
        assert_eq!(Decision::Allow, decision("allow").ok().unwrap().1);
        assert_eq!(Decision::Deny, decision("deny").ok().unwrap().1);
        assert_eq!(Decision::AllowLog, decision("allow_log").ok().unwrap().1);
        assert_eq!(Decision::DenyLog, decision("deny_log").ok().unwrap().1);
        assert_eq!(Decision::DenyAudit, decision("deny_audit").ok().unwrap().1);
        assert_eq!(
            Decision::AllowAudit,
            decision("allow_audit").ok().unwrap().1
        );
    }

    // todo;; need better error propagation, and then better negative tests
    #[test]
    fn bad_rules() {
        rule("deny_audit perm=open all : foo").err().unwrap();
        rule("deny_audit perm=open all trust=foo : all")
            .err()
            .unwrap();

        let (rem, _) = rule("deny_audit perm=open all : all trust=1 foo")
            .ok()
            .unwrap();
        assert!(!rem.is_empty());

        let (rem, _) = rule("deny_audit perm=open all : all trust=foo")
            .ok()
            .unwrap();
        assert!(!rem.is_empty());
    }

    #[test]
    fn parse_rule() {
        let (rem, r) = rule("deny_audit perm=any pattern=ld_so : all")
            .ok()
            .unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Any, r.perm);
        assert_eq!(Subject::from(SubjPart::Pattern("ld_so".into())), r.subj);
        assert_eq!(Object::from(ObjPart::All), r.obj);
        assert!(rem.is_empty());

        let (rem, r) = rule("deny_audit perm=any all : all").ok().unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Any, r.perm);
        assert_eq!(Subject::from(SubjPart::All), r.subj);
        assert_eq!(Object::from(ObjPart::All), r.obj);
        assert!(rem.is_empty());

        let (rem, r) = rule("deny_audit perm=open all : device=/dev/cdrom")
            .ok()
            .unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Open, r.perm);
        assert_eq!(Subject::from(SubjPart::All), r.subj);
        assert_eq!(Object::from(ObjPart::Device("/dev/cdrom".into())), r.obj);
        assert!(rem.is_empty());

        let (rem, r) = rule("deny_audit perm=open exe=/usr/bin/ssh : dir=/opt")
            .ok()
            .unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Open, r.perm);
        assert_eq!(Subject::from(SubjPart::Exe("/usr/bin/ssh".into())), r.subj);
        assert_eq!(Object::from(ObjPart::Dir("/opt".into())), r.obj);
        assert!(rem.is_empty());

        let (rem, r) = rule("deny_audit perm=any all : ftype=application/x-bad-elf")
            .ok()
            .unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Any, r.perm);
        assert_eq!(Subject::from(SubjPart::All), r.subj);
        assert_eq!(
            Object::from(ObjPart::FileType(Literal("application/x-bad-elf".into()))),
            r.obj
        );
        assert!(rem.is_empty());
    }

    #[test]
    fn parse_set() {
        let def = "%lang=application/x-bytecode.ocaml,application/x-bytecode.python,application/java-archive,text/x-java";
        let md = set(def).ok().unwrap().1;

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
        assert_eq!(false, trust_flag("0").ok().unwrap().1);
        assert_eq!(true, trust_flag("1").ok().unwrap().1);
        assert_eq!(None, trust_flag("2").ok());
        assert_eq!(None, trust_flag("foo").ok());
    }
}
