/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */


use nom::bytes::complete::{is_not, tag};







use nom::sequence::{preceded};










use crate::parser::parse::{StrTrace, TraceResult};

pub fn parse(i: StrTrace) -> TraceResult<String> {
    match nom::combinator::complete(preceded(tag("#"), is_not("\n")))(i) {
        Ok((remaining, c)) => Ok((remaining, c.fragment.to_string())),
        Err(e) => Err(e),
    }
}
