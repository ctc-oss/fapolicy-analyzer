/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use nom::bytes::complete::{is_not, tag};

use nom::character::complete::alphanumeric1;

use nom::multi::separated_list1;
use nom::sequence::separated_pair;

use crate::set::Set;

use crate::parser::parse::{StrTrace, TraceResult};

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
