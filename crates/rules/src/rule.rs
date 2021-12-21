/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fmt::{Display, Formatter};
use std::str::FromStr;

use crate::{parse, Decision, Object, Permission, Subject};

/// # Rule
/// A Rule is used by fapolicyd to make decisions about access rights. The rules follow a simple format of:
/// ### `decision perm subject : object`
///
/// They are evaluated from top to bottom with the first rule to match being used for the access control decision.
/// The colon is mandatory to separate subject and object since they share keywords.
///
/// ### Currently only v2 rule format is supported.
///
#[derive(Clone, Debug)]
pub struct Rule {
    pub subj: Subject,
    pub perm: Permission,
    pub obj: Object,
    pub dec: Decision,
}

impl Rule {
    pub fn new(subj: Subject, perm: Permission, obj: Object, dec: Decision) -> Self {
        Rule {
            subj,
            perm,
            obj,
            dec,
        }
    }

    pub fn allow(subj: Subject, perm: Permission, obj: Object) -> Self {
        Self::new(subj, perm, obj, Decision::Allow)
    }

    pub fn deny(subj: Subject, perm: Permission, obj: Object) -> Self {
        Self::new(subj, perm, obj, Decision::DenyAudit)
    }
}

impl Display for Rule {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.write_fmt(format_args!(
            "{} {} {} : {}",
            self.dec, self.perm, self.subj, self.obj
        ))
    }
}

impl FromStr for Rule {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match parse::rule(s) {
            Ok((_, r)) => Ok(r),
            Err(_) => Err("Failed to parse Rule from string".into()),
        }
    }
}

#[cfg(test)]
mod tests {
    use crate::object::Part as ObjPart;
    use crate::subject::Part as SubjPart;

    use super::*;

    #[test]
    fn display() {
        let r = Rule::deny(
            Subject::from(SubjPart::All),
            Permission::Open,
            Object::from(ObjPart::All),
        );
        let expected = "deny_audit perm=open all : all";

        assert_eq!(expected, format!("{}", r));
    }
}
