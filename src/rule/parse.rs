use nom::branch::alt;
use nom::bytes::complete::tag;
use nom::character::complete::digit1;
use nom::character::complete::space0;
use nom::character::complete::space1;
use nom::character::is_alphanumeric;
use nom::combinator::map;
use nom::sequence::{separated_pair, terminated};

use crate::rule::{Decision, Object, Permission, Rule, Subject};

fn decision(i: &str) -> nom::IResult<&str, Decision> {
    alt((
        map(tag("allow"), |_| Decision::Allow),
        map(tag("deny_audit"), |_| Decision::DenyAudit),
        map(tag("deny"), |_| Decision::Deny),
    ))(i)
}

fn permission(i: &str) -> nom::IResult<&str, Permission> {
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

fn subject(i: &str) -> nom::IResult<&str, Subject> {
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

fn object(i: &str) -> nom::IResult<&str, Object> {
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
        Ok((remaining_input, (d, p, s, _, o))) => Ok((remaining_input, Rule::new(s, p, o, d))),
        Err(e) => Err(e),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

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
    }
}
