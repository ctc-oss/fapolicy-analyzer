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

use crate::parser::parse::{NomTraceError, StrTrace, TraceError, TraceResult};

pub fn parse(i: StrTrace) -> TraceResult<Set> {
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
            Set::new(
                var.fragment,
                def.iter().map(|s| s.fragment.to_string()).collect(),
            ),
        )),
        Err(e) => Err(e),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_set() {
        let def = "%lang=application/x-bytecode.ocaml,application/x-bytecode.python,application/java-archive,text/x-java";
        let md = parse(def.into()).ok().unwrap().1;

        assert_eq!("lang", md.name);
        assert_eq!(
            vec![
                "application/x-bytecode.ocaml",
                "application/x-bytecode.python",
                "application/java-archive",
                "text/x-java"
            ],
            md.values
        );
    }
}
