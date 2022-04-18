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

use crate::parser::parse::{
    end_of_rule, subject_object_parts, NomTraceError, StrTrace, TraceError, TraceResult,
};
use crate::parser::{decision, permission};

pub fn parse(i: StrTrace) -> TraceResult<Rule> {
    match nom::combinator::complete(nom::sequence::tuple((
        terminated(decision::parse, space1),
        terminated(permission::parse, space0),
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

#[cfg(test)]
mod tests {
    use super::*;

    // todo;; need better error propagation, and then better negative tests
    #[test]
    fn bad_rules() {
        parse("deny_audit perm=open all : foo".into())
            .err()
            .unwrap();
        parse("deny_audit perm=open all trust=foo : all".into())
            .err()
            .unwrap();

        parse("deny_audit perm=open all : all trust=1 foo".into())
            .err()
            .unwrap();

        parse("deny_audit perm=open all : all trust=foo".into())
            .err()
            .unwrap();
    }

    #[test]
    fn parse_rule() {
        let (rem, r) = parse("deny_audit perm=any pattern=ld_so : all".into())
            .ok()
            .unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Any, r.perm);
        assert_eq!(Subject::from(SubjPart::Pattern("ld_so".into())), r.subj);
        assert_eq!(Object::from(ObjPart::All), r.obj);
        assert!(rem.is_empty());

        let (rem, r) = parse("deny_audit perm=any all : all".into()).ok().unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Any, r.perm);
        assert_eq!(Subject::from(SubjPart::All), r.subj);
        assert_eq!(Object::from(ObjPart::All), r.obj);
        assert!(rem.is_empty());

        let (rem, r) = parse("deny_audit perm=open all : device=/dev/cdrom".into())
            .ok()
            .unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Open, r.perm);
        assert_eq!(Subject::from(SubjPart::All), r.subj);
        assert_eq!(Object::from(ObjPart::Device("/dev/cdrom".into())), r.obj);
        assert!(rem.is_empty());

        let (rem, r) = parse("deny_audit perm=open exe=/usr/bin/ssh : dir=/opt".into())
            .ok()
            .unwrap();
        assert_eq!(Decision::DenyAudit, r.dec);
        assert_eq!(Permission::Open, r.perm);
        assert_eq!(Subject::from(SubjPart::Exe("/usr/bin/ssh".into())), r.subj);
        assert_eq!(Object::from(ObjPart::Dir("/opt".into())), r.obj);
        assert!(rem.is_empty());

        let (rem, r) = parse("deny_audit perm=any all : ftype=application/x-bad-elf".into())
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
}
