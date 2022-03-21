use std::error::Error;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::ops::Range;
use std::path::PathBuf;

use ariadne::Source;
use ariadne::{Report, ReportKind};
use clap::Clap;
use nom::IResult;

use fapolicy_app::cfg;
use fapolicy_rules::parse::{rule, StrTrace};
use fapolicy_rules::parser::errat::{ErrorAt, StrErrorAt};
use fapolicy_rules::parser::trace::Trace;
use fapolicy_rules::Rule;

use crate::Line::{Blank, Comment, RuleDef, SetDec};

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
    let sys_conf = cfg::All::load()?;
    let all_opts: Opts = Opts::parse();

    let rules_path = &*all_opts.rules_path;
    let path = PathBuf::from(rules_path);
    let reader = File::open(path).map(BufReader::new)?;

    let contents: Result<Vec<String>, std::io::Error> = reader.lines().collect();
    let contents: Vec<String> = contents?
        .into_iter()
        .map(|s| s.trim().to_string())
        //.filter(|s| !s.is_empty() && !s.starts_with('#'))
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
            } else if s.starts_with("#") {
                Comment(s.clone())
            } else if s.starts_with("%") {
                SetDec
            } else {
                let x = rule(Trace::new(&s)).map_err(|e| match e {
                    nom::Err::Error(e) => ErrorAt::from(e),
                    e => panic!("hmmmmmmmmmmmmmmmmmmmmmmm"),
                });
                RuleDef(x)
            }
        })
        .enumerate()
        .filter_map(|(i, r)| match r {
            RuleDef(r) => Some((
                i,
                r.map_err(|e| nom::Err::Error(ErrorAt(e.0, e.1 + offsets[i].start, e.2))),
            )),
            x => None,
        })
        .collect();

    if results.iter().all(|(_, r)| r.as_ref().is_ok()) {
        println!("Valid!");
    } else {
        for (lineno, result) in results {
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
