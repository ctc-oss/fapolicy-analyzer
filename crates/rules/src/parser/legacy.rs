use crate::parse::{StrTrace, TraceError};
use crate::{parse, Decision, Object, Permission, Subject};
use nom::bytes::complete::{is_not, take_until};
use nom::bytes::streaming::tag;
use nom::character::complete::space0;
use nom::combinator::rest;
use nom::error::ErrorKind;
use nom::sequence::tuple;
use nom::Err;

// provide legacy api to the new parsers

pub fn decision(i: &str) -> nom::IResult<&str, Decision> {
    match parse::decision(StrTrace::new(i)) {
        Ok((r, d)) => Ok((r.fragment, d)),
        Err(e) => Err(nom::Err::Error(nom::error::Error {
            input: i,
            code: ErrorKind::CrLf,
        })),
    }
}
pub fn permission(i: &str) -> nom::IResult<&str, Permission> {
    match parse::permission(StrTrace::new(i)) {
        Ok((r, p)) => Ok((r.fragment, p)),
        Err(e) => Err(nom::Err::Error(nom::error::Error {
            input: i,
            code: ErrorKind::CrLf,
        })),
    }
}
pub fn subject(i: &str) -> nom::IResult<&str, Subject> {
    let (r, ss) = take_until(" :")(StrTrace::new(i)).map_err(|e: Err<TraceError>| {
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
        .map_err(|e: Err<TraceError>| {
            nom::Err::Error(nom::error::Error {
                input: i,
                code: ErrorKind::Alpha,
            })
        })?;

    match parse::object(oo) {
        Ok((r, o)) => Ok((r.fragment, o)),
        Err(e) => Err(nom::Err::Error(nom::error::Error {
            input: i,
            code: ErrorKind::Alt,
        })),
    }
}
