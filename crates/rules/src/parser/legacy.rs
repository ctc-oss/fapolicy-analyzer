use crate::parse::{StrTrace, TraceError};
use crate::parser::error::RuleParseError;
use crate::parser::trace::Trace;
use crate::{parse, Decision, Object, Permission, Subject};
use nom::error::ErrorKind;
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
    match parse::subject(StrTrace::new(i)) {
        Ok((r, s)) => Ok((r.fragment, s)),
        Err(e) => Err(nom::Err::Error(nom::error::Error {
            input: i,
            code: ErrorKind::CrLf,
        })),
    }
}
pub fn object(i: &str) -> nom::IResult<&str, Object> {
    match parse::object(StrTrace::new(i)) {
        Ok((r, o)) => Ok((r.fragment, o)),
        Err(e) => Err(nom::Err::Error(nom::error::Error {
            input: i,
            code: ErrorKind::CrLf,
        })),
    }
}
