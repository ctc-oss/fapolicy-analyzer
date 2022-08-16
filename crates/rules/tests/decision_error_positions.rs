/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use fapolicy_rules::parser::errat::ErrorAt;
use fapolicy_rules::parser::rule;

use fapolicy_rules::parser::error::RuleParseError::{ExpectedDecision, UnknownDecision};
use nom::Err::Error;

#[test]
fn prefix() {
    if let Error(e) = rule::parse("xdeny_audit perm=any pattern=ld_so : all".into())
        .err()
        .unwrap()
    {
        let e = ErrorAt::from(e);
        assert!(matches!(e.0, UnknownDecision(_, _)));
        assert_eq!(e.1, 0);
        assert_eq!(e.2, "xdeny_audit".len());
    } else {
        panic!();
    }
}

#[test]
fn suffix() {
    let txt = "deny_foo perm=any pattern=ld_so : all";
    if let Error(e) = rule::parse(txt.into()).err().unwrap() {
        let e = ErrorAt::from(e);
        assert!(matches!(e.0, ExpectedDecision(_)));
        assert_eq!(e.1, 0);
        assert_eq!(e.2, txt.len());
    } else {
        panic!();
    }
}

#[test]
fn unknown() {
    if let Error(e) = rule::parse("foo perm=any pattern=ld_so : all".into())
        .err()
        .unwrap()
    {
        let e = ErrorAt::from(e);
        assert!(matches!(e.0, UnknownDecision(_, _)));
        assert_eq!(e.1, 0);
        assert_eq!(e.2, "foo".len());
    } else {
        panic!();
    }
}
