use crate::rule::{Decision, Object, Permission, Subject};
use std::fmt::{Display, Formatter};

pub struct Rule {
    s: Subject,
    p: Permission,
    o: Object,
    d: Decision,
}

impl Rule {
    pub fn allow(s: Subject, p: Permission, o: Object) -> Rule {
        Rule {
            s,
            p,
            o,
            d: Decision::Deny,
        }
    }

    pub fn deny(s: Subject, p: Permission, o: Object) -> Rule {
        Rule {
            s,
            p,
            o,
            d: Decision::DenyAudit,
        }
    }
}

impl Display for Rule {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.write_fmt(format_args!(
            "{} {} {} : {}",
            self.d, self.p, self.s, self.o
        ))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    //deny_audit perm=any all                : device=/dev/cdrom
    //deny_audit perm=execute all            : ftype=any
    //deny_audit perm=open exe=/usr/bin/ssh : dir=/opt
    //deny_audit perm=any pattern=ld_so : all

    #[test]
    fn display() {
        let r = Rule::deny(Subject::All, Permission::Open, Object::All);
        let expected = "deny_audit perm=open all : all";

        assert_eq!(expected, format!("{}", r));
    }
}
