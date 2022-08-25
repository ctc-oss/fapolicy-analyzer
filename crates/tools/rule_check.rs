// Copyright Concurrent Technologies Corporation 2021
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

use std::error::Error;
use std::ops::Range;
use std::path::PathBuf;

use ariadne::Source;
use ariadne::{Report, ReportKind};
use clap::Clap;

use fapolicy_rules::parser::errat::{ErrorAt, StrErrorAt};
use fapolicy_rules::parser::parse::StrTrace;
use fapolicy_rules::parser::trace::Trace;
use fapolicy_rules::{load, Rule};

use crate::Line::{Blank, Comment, RuleDef, SetDec};
use fapolicy_rules::parser::rule;
use nom::IResult;
use std::collections::BTreeMap;
use std::fs::File;
use std::io;
use std::io::{BufRead, BufReader};

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
    let contents: BTreeMap<PathBuf, Vec<String>> = load::rules_from_disk(rules_path)?
        .into_iter()
        .fold(BTreeMap::new(), |mut x, (p, t)| {
            if !x.contains_key(&p) {
                x.insert(p.clone(), vec![]);
            }
            x.get_mut(&p).unwrap().push(t);
            x
        });

    for (file, _) in contents {
        report_for_file(file)?;
    }
    Ok(())
}

fn report_for_file(path: PathBuf) -> Result<(), Box<dyn Error>> {
    let filename = path.display().to_string();
    let buff = BufReader::new(File::open(path)?);
    let lines: Result<Vec<String>, io::Error> = buff.lines().collect();

    let contents: Vec<String> = lines?.into_iter().collect();

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
                let x = rule::parse(Trace::new(s)).map_err(|e| match e {
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

    for (lineno, result) in results {
        if result.is_err() {
            let r = to_ariadne_labels(&filename, result).into_iter().rfold(
                Report::build(ReportKind::Error, filename.as_str(), offsets[lineno].start),
                |r, l| r.with_label(l),
            );

            r.finish()
                .print((filename.as_str(), Source::from(contents.join("\n"))))
                .unwrap();
        }
    }

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
            // eprintln!("e: {:?}", e.1..e.2);
            Some(ariadne::Label::new((id, e.1..e.2)).with_message(format!("{}", e.0)))
        }
        res => {
            eprintln!("unhandled err {:?}", res);
            None
        }
    }
}
