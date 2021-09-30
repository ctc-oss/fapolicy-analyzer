use std::fs::File;
use std::io::{BufRead, BufReader};

use nom::branch::alt;
use nom::combinator::map;

use crate::error::Error;
use crate::rules::db::DB;
use crate::rules::read::Line::{Comment, SetDef, WellFormed};
use crate::rules::{parse, Rule, Set};
use std::collections::HashMap;

enum Line {
    Comment(String),
    SetDef(Set),
    WellFormed(Rule),
}

fn parser(i: &str) -> nom::IResult<&str, Line> {
    alt((
        map(parse::comment, Comment),
        map(parse::set, SetDef),
        map(parse::rule, WellFormed),
    ))(i)
}

pub fn load_rules_db(path: &str) -> Result<DB, Error> {
    let f = File::open(path).expect("failed to open file");
    let buff = BufReader::new(f);

    let xs: Vec<String> = buff
        .lines()
        .map(|r| r.unwrap())
        .filter(|s| !s.is_empty() && !s.starts_with('#'))
        .collect();

    let lookup: HashMap<usize, Rule> = xs
        .iter()
        .map(|l| (l, parser(l)))
        .flat_map(|(_, r)| match r {
            Ok(("", rule)) => Some(rule),
            Ok((_, _)) => None,
            Err(_) => None,
        })
        .filter_map(|line| match line {
            WellFormed(r) => Some(r),
            _ => None,
        })
        .enumerate()
        // fapolicyd rules are indexed from 1
        .map(|(k, v)| (k + 1, v))
        .collect();

    for r in lookup.iter() {
        println!("{}: {}", r.0, r.1);
    }
    println!("loaded {} rules", lookup.len());

    Ok(DB { lookup })
}
