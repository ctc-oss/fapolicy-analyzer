/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::error::Error;
use std::ops::Range;
use std::path::PathBuf;

use ariadne::Source;
use ariadne::{Report, ReportKind};
use clap::Clap;

use fapolicy_rules::parse::{rule, StrTrace};
use fapolicy_rules::parser::errat::{ErrorAt, StrErrorAt};
use fapolicy_rules::parser::trace::Trace;
use fapolicy_rules::{load, Rule};

use crate::Line::{Blank, Comment, RuleDef, SetDec};
use nom::IResult;

#[derive(Clap)]
#[clap(name = "Rule Checker", version = "v0.0.0")]
struct Opts {
    /// path to *.rules or rules.d
    rules_path: String,
}

type RuleParse<'a> = Result<(StrTrace<'a>, Rule), ErrorAt<StrTrace<'a>>>;

enum Line<'a> {
    Blank,
    Comment(String),
    SetDec,
    RuleDef(RuleParse<'a>),
}

fn main() -> Result<(), Box<dyn Error>> {
    let all_opts: Opts = Opts::parse();

    let rules_path = &*all_opts.rules_path;
    let path = PathBuf::from(rules_path);
    let contents: Vec<(PathBuf, String)> = load::rules_from(path)?;

    let contents: Vec<String> = contents
        .into_iter()
        .map(|(_, s)| s.trim().to_string())
        .collect();

    let offsets = contents
        .iter()
        .fold(vec![], |mut a: Vec<Range<usize>>, curr| {
            let prev = a.last().unwrap_or(&(0..0));
            let start = match prev.end {
                0 => 0,
                v => v + 1,
            };
            let end = start + curr.len();
            a.push(start..end);
            a
        });

    offsets.iter().for_each(|o| println!("offset: {:?}", o));

    let results: Vec<(usize, IResult<StrTrace, Rule, StrErrorAt>)> = contents
        .iter()
        .map(|s| {
            if s.trim().is_empty() {
                Blank
            } else if s.starts_with('#') {
                Comment(s.clone())
            } else if s.starts_with('%') {
                SetDec
            } else {
                let x = rule(Trace::new(s)).map_err(|e| match e {
                    nom::Err::Error(e) => ErrorAt::from(e),
                    _ => panic!("unexpectd error state"),
                });
                RuleDef(x)
            }
        })
        .enumerate()
        .filter_map(|(i, r)| match r {
            RuleDef(r) => Some((i, r.map_err(|e| nom::Err::Error(e.shift(offsets[i].start))))),
            _ => None,
        })
        .collect();

    if results.iter().all(|(_, r)| r.as_ref().is_ok()) {
        println!("Valid!");
    } else {
        for (_lineno, result) in results {
            let r = to_ariadne_labels(rules_path, result)
                .into_iter()
                .rfold(Report::build(ReportKind::Error, rules_path, 0), |r, l| {
                    r.with_label(l)
                });

            r.finish()
                .print((rules_path, Source::from(contents.join("\n"))))
                .unwrap();
        }
    }

    // todo;; error code on invalid rules
    Ok(())
}

fn to_ariadne_labels<'a>(
    id: &'a str,
    result: IResult<StrTrace, Rule, StrErrorAt>,
) -> Option<ariadne::Label<(&'a str, Range<usize>)>> {
    match result {
        Ok(_) => None,
        Err(nom::Err::Error(e)) => {
            // eprintln!("- [!] {:?}", e);
            // eprintln!("e: {:?}", e.1..(e.1 + e.2));
            Some(ariadne::Label::new((id, e.1..(e.1 + e.2))).with_message(format!("{}", e.0)))
        }
        res => {
            eprintln!("unhandled err {:?}", res);
            None
        }
    }
}
