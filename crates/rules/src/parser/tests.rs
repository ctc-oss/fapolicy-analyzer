/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::parser::error::RuleParseError;
use crate::parser::trace::Trace;
use nom::bytes::complete::tag;
use nom::IResult;

#[derive(Debug, Clone)]
struct Product {
    _txt: String,
}

type StrTrace<'a> = Trace<&'a str>;
type StrTraceError<'a> = RuleParseError<StrTrace<'a>>;
type StrTraceResult<'a> = IResult<StrTrace<'a>, Product, StrTraceError<'a>>;

#[test]
fn trace_tag() {
    let r: StrTraceResult = tag("=")(Trace::new("=")).map(|(r, t)| {
        (
            r,
            Product {
                _txt: t.current.to_string(),
            },
        )
    });
    assert!(r.is_ok());
    let (x, y) = r.ok().unwrap();
    println!("{:?} {:?}", x, y);
}
