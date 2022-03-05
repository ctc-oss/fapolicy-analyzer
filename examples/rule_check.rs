#![allow(dead_code)]
#![allow(unused_variables)]

extern crate nom;

use std::fmt::{Display, Formatter};
use std::io;
use std::io::BufRead;

use codespan_reporting::diagnostic::{Diagnostic, Label};
use codespan_reporting::files::SimpleFiles;
use codespan_reporting::term;
use codespan_reporting::term::termcolor::{ColorChoice, StandardStream};
use nom::branch::alt;
use nom::bytes::complete::tag;
use nom::character::complete::{alphanumeric1, space0, space1};
use nom::combinator::{eof, map, opt};
use nom::error::ErrorKind;
use nom::error::ParseError;
use nom::sequence::{terminated, tuple};
use nom::{Err, IResult};

use crate::CustomError::*;

#[derive(Debug, PartialEq, Copy, Clone)]
pub enum CustomError<I> {
    ExpectedDecision(I, usize),
    UnknownDecision(I, usize),
    ExpectedPermTag(I, usize),
    ExpectedPermType(I, usize),
    ExpectedPermAssignment(I, usize),
    ExpectedEndOfInput(I, usize),
    ExpectedWhitespace(I, usize),
    Nom(I, ErrorKind),
}

impl Display for CustomError<&str> {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            ExpectedDecision(_, _) => f.write_str("Expected Decision"),
            UnknownDecision(_, _) => f.write_str("Unknown Decision"),
            ExpectedPermTag(_, _) => f.write_str("Expected tag 'perm'"),
            ExpectedPermType(_, _) => f.write_str("Expected one of 'any', 'open', 'execute'"),
            ExpectedPermAssignment(_, _) => f.write_str("Expected assignment (=)"),
            ExpectedEndOfInput(_, _) => f.write_str("Unexpected trailing chars"),
            ExpectedWhitespace(_, _) => f.write_str("Expected whitespace"),
            other => f.write_fmt(format_args!("{:?}", other)),
        }
    }
}

#[derive(Debug, PartialEq, Copy, Clone)]
pub struct ErrorAt<I>(CustomError<I>, usize, usize);

impl<I> ParseError<I> for CustomError<I> {
    fn from_error_kind(input: I, kind: ErrorKind) -> Self {
        CustomError::Nom(input, kind)
    }

    fn append(s: I, e: ErrorKind, other: Self) -> Self {
        other
    }
}

// fn parse(input: &str) -> IResult<&str, &str, CustomError<&str>> {
//     Err(Error(CustomError::MyError))
// }

#[derive(Clone, Debug, PartialEq)]
pub enum Decision {
    AllowAudit,
    AllowSyslog,
    AllowLog,
    Allow,
    Deny,
    DenyLog,
    DenyAudit,
    DenySyslog,
}

#[derive(Clone, Debug, PartialEq)]
pub enum Permission {
    Any,
    Open,
    Execute,
}

pub fn parse_allow(i: &str) -> nom::IResult<&str, Decision> {
    map(tag("allow"), |_| Decision::Allow)(i)
}
pub fn parse_deny(i: &str) -> nom::IResult<&str, Decision> {
    map(tag("deny"), |_| Decision::Deny)(i)
}

pub fn parse_perm_any(i: &str) -> nom::IResult<&str, Permission> {
    map(tag("any"), |_| Permission::Any)(i)
}
pub fn parse_perm_open(i: &str) -> nom::IResult<&str, Permission> {
    map(tag("open"), |_| Permission::Open)(i)
}
pub fn parse_perm_execute(i: &str) -> nom::IResult<&str, Permission> {
    map(tag("execute"), |_| Permission::Execute)(i)
}

pub fn decision(i: &str) -> nom::IResult<&str, Decision, CustomError<&str>> {
    match nom::combinator::complete(alt((parse_allow, parse_deny)))(i) {
        Ok((r, dec)) => Ok((r, dec)),
        Err(e) => {
            let guessed = i
                .split_once(" ")
                .map(|x| UnknownDecision(x.0, i.len()))
                .unwrap_or_else(|| {
                    ExpectedDecision(
                        i.clone().split_once(" ").map(|x| x.0).unwrap_or_else(|| i),
                        i.len(),
                    )
                });
            Err(nom::Err::Error(guessed))
        }
    }
}

pub fn parse_perm_tag(i: &str) -> nom::IResult<&str, (), CustomError<&str>> {
    match nom::combinator::complete(tuple((alphanumeric1, opt(tag("=")))))(i) {
        Ok((r, (k, eq))) if k == "perm" => {
            if eq.is_some() {
                Ok((r, ()))
            } else {
                Err(nom::Err::Error(ExpectedPermAssignment(k, i.len() - 4)))
            }
        }
        Ok((r, (k, _))) => Err(nom::Err::Error(ExpectedPermTag(k, i.len()))),
        Err(e) => Err(e),
    }
}

pub fn parse_perm_opts(i: &str) -> nom::IResult<&str, Permission, CustomError<&str>> {
    match opt(alt((parse_perm_any, parse_perm_open, parse_perm_execute)))(i) {
        Ok((r, Some(p))) => Ok((r, p)),
        Ok((r, None)) => Err(nom::Err::Error(ExpectedPermType(i, i.len()))),
        _ => Err(nom::Err::Error(ExpectedPermType(i, i.len()))),
    }
}

pub fn end_of_rule(i: &str) -> nom::IResult<&str, (), CustomError<&str>> {
    eof::<&str, CustomError<&str>>(i)
        .map(|x| (x.0, ()))
        .map_err(|_| nom::Err::Error(ExpectedEndOfInput(i, i.len())))
}

pub fn permission(i: &str) -> nom::IResult<&str, Permission, CustomError<&str>> {
    match nom::combinator::complete(nom::sequence::tuple((parse_perm_tag, parse_perm_opts)))(i) {
        Ok((r, (_, p))) => Ok((r, p)),
        Err(e) => Err(e),
    }
}

impl<T, I> Into<Result<T, nom::Err<ErrorAt<I>>>> for ErrorAt<I> {
    fn into(self) -> Result<T, nom::Err<ErrorAt<I>>> {
        Err(nom::Err::Error(self))
    }
}

#[derive(Debug)]
pub struct Both {
    dec: Decision,
    perm: Permission,
}

pub fn both(i: &str) -> nom::IResult<&str, Both, ErrorAt<&str>> {
    let fulllen = i.len();

    match nom::combinator::complete(nom::sequence::tuple((
        terminated(decision, space1),
        terminated(permission, space0),
        end_of_rule,
    )))(i)
    {
        Ok((remaining_input, (dec, perm, _))) => Ok((remaining_input, Both { dec, perm })),
        Err(Err::Error(ref e)) => match e {
            ee @ ExpectedDecision(ii, pos) => ErrorAt(*ee, fulllen - *pos, ii.len()).into(),
            ee @ UnknownDecision(ii, pos) => ErrorAt(*ee, fulllen - *pos, ii.len()).into(),
            ee @ ExpectedPermTag(ii, pos) => ErrorAt(*ee, fulllen - *pos, ii.len()).into(),
            ee @ ExpectedPermType(ii, pos) => ErrorAt(*ee, fulllen - *pos, *pos).into(),
            ee @ ExpectedPermAssignment(ii, pos) => ErrorAt(*ee, fulllen - *pos, 0).into(),
            ee @ ExpectedEndOfInput(ii, pos) => ErrorAt(*ee, fulllen - *pos, ii.len()).into(),
            ee @ ExpectedWhitespace(ii, pos) => ErrorAt(*ee, fulllen - *pos, ii.len()).into(),
            ee @ Nom(ii, ErrorKind::Space) => {
                let at = fulllen - ii.len();
                Err(nom::Err::Error(ErrorAt(ExpectedWhitespace(ii, at), at, 0)))
            }
            e => panic!("unhandled pattern {:?}", e),
        },
        e => panic!("unhandled pattern {:?}", e),
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Enter a rule, or Enter to exit...");
    loop {
        let mut contents = vec![];
        loop {
            let line: String = io::stdin()
                .lock()
                .lines()
                .next()
                .unwrap()
                .unwrap()
                .to_string();
            if line.is_empty() {
                break;
            }

            contents.push(line);
        }
        if contents.is_empty() {
            break;
        }

        let mut files = SimpleFiles::new();
        let file_id = files.add("fapolicyd.rules", contents.join("\n"));
        let offsets = contents
            .iter()
            .map(|s| format!("{}\n", s))
            .fold(vec![0], |a, b| {
                let off: usize = a.iter().sum();
                let mut aa = a.clone();
                aa.push(off + b.len());
                aa
            });

        let results: Vec<IResult<&str, Both, ErrorAt<&str>>> = contents
            .iter()
            .map(|s| both(&s))
            .enumerate()
            .map(|(i, r)| match r {
                ok @ Ok(_) => ok,
                Err(nom::Err::Error(e)) => ErrorAt(e.0, e.1 + offsets[i], e.2).into(),
                _ => panic!("unhandled"),
            })
            .collect();

        to_diagnostic(file_id, results).map(|d| emit_diagnostic(&files, d));
    }

    Ok(())
}

fn emit_diagnostic(
    files: &SimpleFiles<&'static str, String>,
    d: Diagnostic<usize>,
) -> Result<(), Box<dyn std::error::Error>> {
    let writer = StandardStream::stderr(ColorChoice::Always);
    let config = codespan_reporting::term::Config::default();
    term::emit(&mut writer.lock(), &config, files, &d)?;

    Ok(())
}

fn to_diagnostic(
    file_id: usize,
    results: Vec<IResult<&str, Both, ErrorAt<&str>>>,
) -> Option<Diagnostic<usize>> {
    if results.iter().all(|r| r.as_ref().is_ok()) {
        println!("Valid!");
        None
    } else {
        let labels: Vec<Label<usize>> = results
            .iter()
            .map(|e| match e {
                Err(nom::Err::Error(e)) => {
                    Some(Label::primary(file_id, e.1..(e.1 + e.2)).with_message(format!("{}", e.0)))
                }
                Ok(_) => None,
                _ => panic!("ugh"),
            })
            .flatten()
            .collect();

        Some(
            Diagnostic::error()
                .with_message("failed to compile rule")
                .with_labels(labels)
                .with_notes(vec![unindent::unindent(
                    "
            check the fapolicyd rules man page,
                https://www.mankier.com/5/fapolicyd.rules
        ",
                )]),
        )
    }
}
