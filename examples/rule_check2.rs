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
use nom::combinator::rest;
use nom::sequence::terminated;
use nom::{Err, IResult};

use fapolicy_rules::parse::{rule, StrTrace};
use fapolicy_rules::parser::errat::{ErrorAt, StrErrorAt};
use fapolicy_rules::parser::error::RuleParseError;
use fapolicy_rules::parser::error::RuleParseError::*;
use fapolicy_rules::parser::legacy::{decision, permission};
use fapolicy_rules::parser::trace::{Position, Trace};
use fapolicy_rules::Rule;

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

        let results: Vec<IResult<StrTrace, Rule, StrErrorAt>> = contents
            .iter()
            .map(|s| {
                rule(Trace::new(&s)).map_err(|e| match e {
                    Err::Error(e) => ErrorAt::from(e),
                    e => panic!("hmmmmmmmmmmmmmmmmmmmmmmm"),
                })
            })
            .enumerate()
            .map(|(i, r)| match r {
                Err(e) => Err(nom::Err::Error(ErrorAt(e.0, e.1 + offsets[i], e.2))),
                Ok(x) => Ok(x),
                res => panic!("grrrrrrrrrrrrrrrrrrrrrrr"),
                //res => res,
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
    results: Vec<IResult<StrTrace, Rule, StrErrorAt>>,
) -> Option<Diagnostic<usize>> {
    if results.iter().all(|r| r.as_ref().is_ok()) {
        println!("Valid!");
        for r in results {
            println!("{:?}", r.ok().unwrap().1);
        }
        None
    } else {
        let labels: Vec<Label<usize>> = results
            .iter()
            .map(|e| match e {
                Ok(_) => None,
                Err(nom::Err::Error(e)) => {
                    Some(Label::primary(file_id, e.1..(e.1 + e.2)).with_message(format!("{}", e.0)))
                }
                res => {
                    println!("unhandled err {:?}", res);
                    None
                }
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
