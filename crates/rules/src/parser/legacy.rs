/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use nom::bytes::complete::{is_not, take_until};
use nom::bytes::streaming::tag;
use nom::character::complete::space0;
use nom::combinator::rest;
use nom::error::ErrorKind;
use nom::sequence::tuple;
use nom::Err;

use crate::parser::parse;
use crate::parser::parse::{StrTrace, TraceError};
use crate::{Decision, Object, Permission, Subject};

// provide legacy api to the new parsers

pub fn decision(i: &str) -> nom::IResult<&str, Decision> {
    match parse::decision(StrTrace::new(i)) {
        Ok((r, d)) => Ok((r.fragment, d)),
        Err(_) => Err(nom::Err::Error(nom::error::Error {
            input: i,
            code: ErrorKind::CrLf,
        })),
    }
}
pub fn permission(i: &str) -> nom::IResult<&str, Permission> {
    match parse::permission(StrTrace::new(i)) {
        Ok((r, p)) => Ok((r.fragment, p)),
        Err(_) => Err(nom::Err::Error(nom::error::Error {
            input: i,
            code: ErrorKind::CrLf,
        })),
    }
}
pub fn subject(i: &str) -> nom::IResult<&str, Subject> {
    let (r, ss) = take_until(" :")(StrTrace::new(i)).map_err(|_: Err<TraceError>| {
        nom::Err::Error(nom::error::Error {
            input: i,
            code: ErrorKind::Alpha,
        })
    })?;
    match parse::subject(ss) {
        Ok((_, s)) => Ok((r.fragment, s)),
        Err(e) => {
            println!("{:?}", e);
            Err(nom::Err::Error(nom::error::Error {
                input: i,
                code: ErrorKind::Alpha,
            }))
        }
    }
}
pub fn object(i: &str) -> nom::IResult<&str, Object> {
    let (_, (_, _, _, oo)) = tuple((is_not(":"), tag(":"), space0, rest))(StrTrace::new(i))
        .map_err(|_: Err<TraceError>| {
            nom::Err::Error(nom::error::Error {
                input: i,
                code: ErrorKind::Alpha,
            })
        })?;

    match parse::object(oo) {
        Ok((r, o)) => Ok((r.fragment, o)),
        Err(_) => Err(nom::Err::Error(nom::error::Error {
            input: i,
            code: ErrorKind::Alt,
        })),
    }
}
