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

use fapolicy_rules::parser::error::RuleParseError;
use fapolicy_rules::parser::error::RuleParseError::*;
use fapolicy_rules::parser::trace::Trace;
use fapolicy_rules::{parsev2, Decision, Permission};

#[derive(Debug, PartialEq, Copy, Clone)]
pub struct ErrorAt<I>(RuleParseError<I>, usize, usize);

type StrTrace<'a> = Trace<&'a str>;
type StrErrorAt<'a> = ErrorAt<StrTrace<'a>>;

pub fn parse_allow(i: StrTrace) -> nom::IResult<StrTrace, Decision> {
    map(tag("allow"), |_| Decision::Allow)(i)
}
pub fn parse_deny(i: StrTrace) -> nom::IResult<StrTrace, Decision> {
    map(tag("deny"), |_| Decision::Deny)(i)
}

pub fn parse_perm_open(i: StrTrace) -> nom::IResult<StrTrace, Permission> {
    map(tag("open"), |_| Permission::Open)(i)
}
pub fn parse_perm_execute(i: StrTrace) -> nom::IResult<StrTrace, Permission> {
    map(tag("execute"), |_| Permission::Execute)(i)
}

pub fn end_of_rule(i: StrTrace) -> nom::IResult<StrTrace, (), RuleParseError<StrTrace>> {
    eof::<StrTrace, RuleParseError<StrTrace>>(i)
        .map(|x| (x.0, ()))
        .map_err(|_| nom::Err::Error(ExpectedEndOfInput /*(i, i.len())*/))
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

pub fn both(i: StrTrace) -> nom::IResult<StrTrace, Both, StrErrorAt> {
    let fulllen = i.fragment.len();

    let pos = &0;
    let ii = "";

    match nom::combinator::complete(nom::sequence::tuple((
        terminated(parsev2::decision, space1),
        terminated(parsev2::permission, space0),
        end_of_rule,
    )))(i)
    {
        Ok((remaining_input, (dec, perm, _))) => Ok((remaining_input, Both { dec, perm })),
        Err(Err::Error(ref e)) => match e {
            ee @ ExpectedDecision/*(ii, pos)*/ => ErrorAt(*ee, fulllen - *pos, ii.len()).into(),
            ee @ UnknownDecision/*(ii, pos)*/ => ErrorAt(*ee, fulllen - *pos, ii.len()).into(),
            ee @ ExpectedPermTag/*(ii, pos)*/ => ErrorAt(*ee, fulllen - *pos, ii.len()).into(),
            ee @ ExpectedPermType/*(ii, pos)*/ => ErrorAt(*ee, fulllen - *pos, *pos).into(),
            ee @ ExpectedPermAssignment/*(ii, pos)*/ => ErrorAt(*ee, fulllen - *pos, 0).into(),
            ee @ ExpectedEndOfInput/*(ii, pos)*/ => ErrorAt(*ee, fulllen - *pos, ii.len()).into(),
            ee @ ExpectedWhitespace/*(ii, pos)*/ => ErrorAt(*ee, fulllen - *pos, ii.len()).into(),
            ee @ Nom(ii, ErrorKind::Space) => {
                let at = fulllen - ii.fragment.len();
                Err(nom::Err::Error(ErrorAt(ExpectedWhitespace/*(ii, at)*/, at, 0)))
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

        let results: Vec<IResult<StrTrace, Both, StrErrorAt>> = contents
            .iter()
            .map(|s| both(Trace::new(&s)))
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
    results: Vec<IResult<StrTrace, Both, StrErrorAt>>,
) -> Option<Diagnostic<usize>> {
    if results.iter().all(|r| r.as_ref().is_ok()) {
        println!("Valid!");
        None
    } else {
        let labels: Vec<Label<usize>> = results
            .iter()
            .map(|e| match e {
                Err(nom::Err::Error(e)) => Some(
                    Label::primary(file_id, e.1..(e.1 + e.2)).with_message(format!("{:?}", e.0)),
                ),
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
