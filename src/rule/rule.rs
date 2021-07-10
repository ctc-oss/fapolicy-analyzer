use crate::rule::{Decision, Object, Permission, Subject};
use std::fmt::{Display, Formatter};

pub struct Rule {
    subject: Subject,
    permission: Permission,
    object: Object,
    decision: Decision,
}

impl Rule {
    fn new(s: Subject, p: Permission, o: Object, d: Decision) -> Rule {
        Rule {
            subject: s,
            permission: p,
            object: o,
            decision: d,
        }
    }
}
