use nom::branch::alt;
use nom::bytes::complete::{is_not, tag};
use nom::character::complete::space0;
use nom::character::complete::space1;
use nom::character::complete::{alphanumeric1, digit1};
use nom::character::is_alphanumeric;
use nom::combinator::map;
use nom::sequence::{separated_pair, terminated};

use crate::rules::file_type::FileType::Mime;
use crate::rules::{Decision, MacroDef, MimeType, Object, Permission, Rule, Subject};
use nom::multi::separated_list1;

pub(crate) fn decision(i: &str) -> nom::IResult<&str, Decision> {
    alt((
        map(tag("allow"), |_| Decision::Allow),
        map(tag("deny_audit"), |_| Decision::DenyAudit),
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

pub(crate) fn subject(i: &str) -> nom::IResult<&str, Subject> {
    alt((
        map(tag("all"), |_| Subject::All),
        map(
            separated_pair(tag("uid"), tag("="), digit1),
            |x: (&str, &str)| Subject::Uid(x.1.parse().unwrap()),
        ),
        map(
            separated_pair(tag("gid"), tag("="), digit1),
            |x: (&str, &str)| Subject::Gid(x.1.parse().unwrap()),
        ),
        map(
            separated_pair(tag("exe"), tag("="), filepath),
            |x: (&str, &str)| Subject::Exe(x.1.to_string()),
        ),
        map(
            separated_pair(tag("pattern"), tag("="), pattern),
            |x: (&str, &str)| Subject::Pattern(x.1.to_string()),
        ),
    ))(i)
}

pub(crate) fn object(i: &str) -> nom::IResult<&str, Object> {
    alt((
        map(tag("all"), |_| Object::All),
        map(
            separated_pair(tag("dir"), tag("="), filepath),
            |x: (&str, &str)| Object::Dir(x.1.to_string()),
        ),
        map(
            separated_pair(tag("device"), tag("="), filepath),
            |x: (&str, &str)| Object::Device(x.1.to_string()),
        ),
        map(
            separated_pair(tag("ftype"), tag("="), filepath),
            |x: (&str, &str)| Object::FileType(Mime(MimeType(x.1.to_string()))),
        ),
    ))(i)
}

fn filepath(i: &str) -> nom::IResult<&str, &str> {
    nom::bytes::complete::is_not(" \t\n")(i)
}

fn pattern(i: &str) -> nom::IResult<&str, &str> {
    nom::bytes::complete::take_while1(|x| is_alphanumeric(x as u8) || x == '_')(i)
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

// todo;; removed this when is used
#[allow(dead_code)]
pub(crate) fn macrodef(i: &str) -> nom::IResult<&str, MacroDef> {
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
            MacroDef::new(var, def.iter().map(|&s| MimeType(s.into())).collect()),
        )),
        Err(e) => Err(e),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::rules::file_type::FileType::Mime;
    use crate::rules::MimeType;

    #[test]
    fn parse_subj() {
        assert_eq!(Subject::All, subject("all").ok().unwrap().1);
        assert_eq!(Subject::Uid(10001), subject("uid=10001").ok().unwrap().1);
        assert_eq!(Subject::Gid(0), subject("gid=0").ok().unwrap().1);
    }

    #[test]
    fn parse_perm() {
        assert_eq!(Permission::Any, permission("perm=any").ok().unwrap().1);
    }

    #[test]
    fn parse_obj() {
        assert_eq!(Object::All, object("all").ok().unwrap().1);
    }

    #[test]
    fn parse_dec() {
        assert_eq!(Decision::DenyAudit, decision("deny_audit").ok().unwrap().1);
    }

    #[test]
    fn parse_rule() {
        let r = rule("deny_audit perm=any pattern=ld_so : all")
            .ok()
            .unwrap()
            .1;
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Any, r.perm);
        assert_eq!(Subject::Pattern("ld_so".into()), r.subj);
        assert_eq!(Object::All, r.obj);

        let r = rule("deny_audit perm=any all : all").ok().unwrap().1;
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Any, r.perm);
        assert_eq!(Subject::All, r.subj);
        assert_eq!(Object::All, r.obj);

        let r = rule("deny_audit perm=open all : device=/dev/cdrom")
            .ok()
            .unwrap()
            .1;
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Open, r.perm);
        assert_eq!(Subject::All, r.subj);
        assert_eq!(Object::Device("/dev/cdrom".into()), r.obj);

        let r = rule("deny_audit perm=open exe=/usr/bin/ssh : dir=/opt")
            .ok()
            .unwrap()
            .1;
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Open, r.perm);
        assert_eq!(Subject::Exe("/usr/bin/ssh".into()), r.subj);
        assert_eq!(Object::Dir("/opt".into()), r.obj);

        let r = rule("deny_audit perm=any all : ftype=application/x-bad-elf")
            .ok()
            .unwrap()
            .1;
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Any, r.perm);
        assert_eq!(Subject::All, r.subj);
        assert_eq!(
            Object::FileType(Mime(MimeType("application/x-bad-elf".into()))),
            r.obj
        );

        //     [fail] deny_audit perm=any all : ftype=application/x-bad-elf
        //     [fail] allow perm=open all : ftype=application/x-sharedlib trust=1
        //     [fail] deny_audit perm=open all : ftype=application/x-sharedlib
        //     [fail] allow perm=execute all : trust=1
        //     [fail] allow perm=open all : ftype=%languages trust=1
        //     [fail] deny_audit perm=any all : ftype=%languages
        //     [fail] allow perm=any all : ftype=text/x-shellscript
    }

    #[test]
    fn parse_macrodef() {
        let def = "%lang=application/x-bytecode.ocaml,application/x-bytecode.python,application/java-archive,text/x-java";
        let md = macrodef(def).ok().unwrap().1;

        assert_eq!("lang", md.name);
        assert_eq!(
            vec![
                "application/x-bytecode.ocaml",
                "application/x-bytecode.python",
                "application/java-archive",
                "text/x-java"
            ]
            .iter()
            .map(|&t| MimeType(t.into()))
            .collect::<Vec<MimeType>>(),
            md.mime
        );
    }
}
