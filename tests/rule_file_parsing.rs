/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fs::File;
use std::io::{BufRead, BufReader};

use nom::branch::alt;
use nom::combinator::map;
use nom::error::ErrorKind;

use fapolicy_rules::parser::parse::StrTrace;
use fapolicy_rules::parser::{comment, rule, set};
use fapolicy_rules::{Rule, Set};

enum Line {
    Acomment(String),
    Arule(Rule),
    Aset(Set),
}

fn parser(i: &str) -> nom::IResult<&str, Line> {
    let ii = StrTrace::new(i);
    match alt((
        map(comment::parse, Line::Acomment),
        map(rule::parse, Line::Arule),
        map(set::parse, Line::Aset),
    ))(ii)
    {
        Ok((r, l)) => Ok((r.current, l)),
        Err(_) => Err(nom::Err::Error(nom::error::Error::new(i, ErrorKind::CrLf))),
    }
}

fn parse_lines(xs: Vec<String>) {
    let lines: Vec<Line> = xs
        .iter()
        .map(|l| (l, parser(l)))
        .flat_map(|(l, r)| match r {
            Ok(("", rule)) => Some(rule),
            Ok((rem, _)) => {
                println!("[incomplete] {} [{}]", l, rem);
                None
            }
            Err(_) => {
                println!("[failure] {}", l);
                None
            }
        })
        .collect();

    for (i, line) in lines.iter().enumerate() {
        match line {
            Line::Acomment(c) => println!("{}: {}", i, c),
            Line::Arule(r) => println!("{}: {}", i, r),
            Line::Aset(m) => println!("{}: {}", i, m),
        }
    }

    println!(
        "{}/{} - {:.2}%",
        lines.len(),
        xs.len(),
        lines.len() as f32 / xs.len() as f32
    );
}

#[test]
fn test_parse_all() {
    let f = File::open("tests/data/rules0.txt").expect("failed to open file");
    let buff = BufReader::new(f);

    let xs: Vec<String> = buff
        .lines()
        .map(|r| r.unwrap())
        .filter(|s| !s.is_empty())
        .collect();

    parse_lines(xs)
}

#[test]
fn test_parse_clean_1() {
    let f = File::open("tests/data/rules1.txt").expect("failed to open file");
    let buff = BufReader::new(f);

    let xs: Vec<String> = buff
        .lines()
        .map(|r| r.unwrap())
        .filter(|s| !s.is_empty() && !s.starts_with('#'))
        .collect();

    parse_lines(xs)
}

#[test]
fn test_parse_clean_2() {
    let f = File::open("tests/data/rules2.txt").expect("failed to open file");
    let buff = BufReader::new(f);

    let xs: Vec<String> = buff
        .lines()
        .map(|r| r.unwrap())
        .filter(|s| !s.is_empty() && !s.starts_with('#'))
        .collect();

    parse_lines(xs)
}
