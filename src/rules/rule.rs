use crate::rules::{parse, Decision, Object, Permission, Subject};
use std::fmt::{Display, Formatter};
use std::str::FromStr;

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
    use super::*;

    #[test]
    fn display() {
        let r = Rule::deny(Subject::All, Permission::Open, Object::All);
        let expected = "deny_audit perm=open all : all";

        assert_eq!(expected, format!("{}", r));
    }
}
