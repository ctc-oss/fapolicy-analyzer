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
use nom::character::complete::{alphanumeric1, space1};
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
        Ok((r, (k, a))) if k == "perm" => {
            if a.is_some() {
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

#[derive(Debug)]
pub struct Both {
    dec: Decision,
    perm: Permission,
}

pub fn both(i: &str) -> nom::IResult<&str, Both, ErrorAt<&str>> {
    let fulllen = i.len();

    match nom::combinator::complete(nom::sequence::tuple((
        terminated(decision, space1),
        permission,
        end_of_rule,
    )))(i)
    {
        Ok((remaining_input, (dec, perm, _))) => Ok((remaining_input, Both { dec, perm })),
        Err(Err::Error(ref e)) => match e {
            ee @ ExpectedDecision(ii, pos) => Err(nom::Err::Error(ErrorAt(
                ee.clone(),
                fulllen - *pos,
                ii.len(),
            ))),
            ee @ UnknownDecision(ii, pos) => Err(nom::Err::Error(ErrorAt(
                ee.clone(),
                fulllen - *pos,
                ii.len(),
            ))),
            ee @ ExpectedPermTag(ii, pos) => Err(nom::Err::Error(ErrorAt(
                ee.clone(),
                fulllen - *pos,
                ii.len(),
            ))),
            ee @ ExpectedPermType(ii, pos) => {
                println!("{} {}", fulllen - pos, pos);
                Err(nom::Err::Error(ErrorAt(ee.clone(), fulllen - *pos, *pos)))
            }
            ee @ ExpectedPermAssignment(ii, pos) => {
                Err(nom::Err::Error(ErrorAt(ee.clone(), fulllen - *pos, 0)))
            }
            ee @ ExpectedEndOfInput(ii, pos) => Err(nom::Err::Error(ErrorAt(
                ee.clone(),
                fulllen - *pos,
                ii.len(),
            ))),
            ee @ ExpectedWhitespace(ii, pos) => Err(nom::Err::Error(ErrorAt(
                ee.clone(),
                fulllen - *pos,
                ii.len(),
            ))),
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
    // println!("{:?}", decision("allow"));

    println!("Enter a rule, or Enter to exit...");
    loop {
        let line: String = io::stdin()
            .lock()
            .lines()
            .next()
            .unwrap()
            .unwrap()
            .trim()
            .to_string();
        if line.is_empty() {
            break;
        }

        let mut files = SimpleFiles::new();
        let file_id = files.add("fapolicyd.rules", line.clone());
        to_diagnostic(file_id, both(&line)).map(|d| emit_diagnostic(&files, d));
    }

    // let mut files = SimpleFiles::new();
    // let file_1 = files.add("fapolicyd.rules", "xallow perm=open".to_string());
    // let file_2 = files.add("fapolicyd.rules", "perm=open".to_string());
    // let file_3 = files.add("fapolicyd.rules", "allow perm=open".to_string());
    // let file_4 = files.add("fapolicyd.rules", "allow perm=openx".to_string());
    // let file_5 = files.add("fapolicyd.rules", "allow pexrm=openx".to_string());

    // println!("1 {:?}", both("xallow perm=open"));
    // println!("2 {:?}", both("perm=open"));
    // println!("3 {:?}", both("allow perm=open"));
    // println!("4 {:?}", both("allow perm=openx"));
    // println!("5 {:?}", both("allow pexrm=openx"));
    // println!("6 {:?}", both("allow perm openx"));
    // println!("7 {:?}", both("deny perm=execute"));

    // to_diagnostic(file_1, both("xallow perm=open")).map(|d| emit_diagnostic(&files, d));
    // to_diagnostic(file_2, both("perm=open")).map(|d| emit_diagnostic(&files, d));
    // to_diagnostic(file_3, both("allow perm=open")).map(|d| emit_diagnostic(&files, d));
    // to_diagnostic(file_4, both("allow perm=openx")).map(|d| emit_diagnostic(&files, d));
    // to_diagnostic(file_5, both("allow pexrm=openx")).map(|d| emit_diagnostic(&files, d));

    // match to_diagnostic(file_id, both("allow perm=openx")) {
    //     None => println!("clean!"),
    //     Some(diagnostic) => emit_diagnostic(files, diagnostic)?,
    // }

    // println!("{:?}", terminated(decision, space1)(" allow".trim()));
    // println!("{:?}", decision("allow foo"));
    //
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
    r: IResult<&str, Both, ErrorAt<&str>>,
) -> Option<Diagnostic<usize>> {
    r.as_ref().ok().map(|_| println!("Valid!"));
    r.err().map(|e| match e {
        nom::Err::Error(e) => Diagnostic::error()
            .with_message("failed to compile rule")
            .with_labels(vec![
                Label::primary(file_id, e.1..(e.1 + e.2)).with_message(format!("{}", e.0))
            ])
            .with_notes(vec![unindent::unindent(
                "
            check the fapolicyd rules man page,
                https://www.mankier.com/5/fapolicyd.rules
        ",
            )]),
        _ => panic!("ugh"),
    })
}
