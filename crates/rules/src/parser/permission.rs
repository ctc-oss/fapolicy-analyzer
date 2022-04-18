/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use nom::branch::alt;
use nom::bytes::complete::{tag};

use nom::character::complete::{alpha1};
use nom::character::complete::{alphanumeric1};

use nom::combinator::{map, opt};


use nom::sequence::{tuple};



use crate::parser::error::RuleParseError::*;



use crate::{Permission};


use crate::parser::parse::{StrTrace, TraceResult};

pub(crate) fn parse(i: StrTrace) -> TraceResult<Permission> {
    // checking the structure of the lhs without deriving any value
    let (ii, _) = match tuple((alphanumeric1, opt(tag("="))))(i) {
        Ok((r, (k, eq))) if k.fragment == "perm" => {
            if eq.is_some() {
                Ok((r, ()))
            } else {
                Err(nom::Err::Error(ExpectedPermAssignment(r)))
            }
        }
        Ok((_, (k, _))) => Err(nom::Err::Error(ExpectedPermTag(i, k))),
        Err(e) => Err(e),
    }?;

    // let (remaining, r) = take_until(" ")(ii)?;
    let (remaining, r) = alpha1(ii)?;
    let res: TraceResult<Option<Permission>> = opt(alt((
        map(tag("any"), |_| Permission::Any),
        map(tag("open"), |_| Permission::Open),
        map(tag("execute"), |_| Permission::Execute),
    )))(r);

    match res {
        Ok((_, Some(p))) => Ok((remaining, p)),
        Ok((r, None)) => Err(nom::Err::Error(ExpectedPermType(ii, r))),
        _ => Err(nom::Err::Error(ExpectedPermType(ii, r))),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_perm() {
        assert_eq!(Permission::Any, parse("perm=any".into()).ok().unwrap().1);
    }
}
