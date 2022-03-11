#![allow(dead_code)]
#![allow(unused_variables)]

extern crate nom;

use std::fmt::Debug;
use std::io;
use std::io::BufRead;

use codespan_reporting::diagnostic::{Diagnostic, Label};
use codespan_reporting::files::SimpleFiles;
use codespan_reporting::term;
use codespan_reporting::term::termcolor::{ColorChoice, StandardStream};
use nom::character::complete::{space0, space1};
use nom::combinator::eof;
use nom::error::ErrorKind;
use nom::sequence::terminated;
use nom::{Err, IResult, InputLength};

use fapolicy_rules::parser::error::RuleParseError;
use fapolicy_rules::parser::error::RuleParseError::*;
use fapolicy_rules::parser::trace::{Position, Trace};
use fapolicy_rules::{parsev2, Decision, Permission};

type StrTrace<'a> = Trace<&'a str>;
type StrErrorAt<'a> = ErrorAt<StrTrace<'a>>;

#[derive(Debug, PartialEq, Copy, Clone)]
pub struct ErrorAt<I>(RuleParseError<I>, usize, usize);

impl ErrorAt<Trace<&str>> {
    pub fn new<'a>(e: RuleParseError<Trace<&'a str>>, t: Trace<&str>) -> ErrorAt<Trace<&'a str>> {
        ErrorAt(e.clone(), t.position(), t.input_len())
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
            ee @ ExpectedDecision(t) => ErrorAt::new(*ee, t.clone()).into(),
            ee @ UnknownDecision(t) => ErrorAt::new(*ee, t.clone()).into(), /*(*ee, fulllen - *pos, ii.len())*/
            ee @ ExpectedPermTag(t) => ErrorAt::new(*ee, t.clone()).into(), /*(*ee, fulllen - *pos, ii.len())*/
            ee @ ExpectedPermType(t) => ErrorAt::new(*ee, t.clone()).into(), /*(*ee, fulllen - *pos, *pos)*/
            ee @ ExpectedPermAssignment(t) => ErrorAt::new(*ee, t.clone()).into(), /*(*ee, fulllen - *pos, 0)*/
            ee @ ExpectedEndOfInput(t) => ErrorAt::new(*ee, t.clone()).into(), /*(*ee, fulllen - *pos, ii.len())*/
            ee @ ExpectedWhitespace(t) => ErrorAt::new(*ee, t.clone()).into(), /*(*ee, fulllen - *pos, ii.len())*/
            ee @ Nom(ii, ErrorKind::Space) => {
                let at = fulllen - ii.fragment.len();
                Err(nom::Err::Error(ErrorAt(
                    ExpectedWhitespace(ii.clone()), /*(ii, at)*/
                    at,
                    0,
                )))
            }
            e => panic!("unhandled pattern {:?}", e),
        },
        e => panic!("unhandled pattern {:?}", e),
    }
}

pub fn end_of_rule(i: StrTrace) -> nom::IResult<StrTrace, (), RuleParseError<StrTrace>> {
    eof::<StrTrace, RuleParseError<StrTrace>>(i)
        .map(|x| (x.0, ()))
        .map_err(|_| nom::Err::Error(ExpectedEndOfInput(i) /*(i, i.len())*/))
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
                    Label::primary(file_id, e.1..(e.1 + e.2))
                        .with_message(format!("{:?} {:?}", e.0, e)),
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
