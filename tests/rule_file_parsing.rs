use crate::Line::{Acomment, Arule, Aset};
use fapolicy_analyzer::rules::{parse, Rule, Set};
use nom::branch::alt;
use nom::combinator::map;
use std::fs::File;
use std::io::{BufRead, BufReader};

enum Line {
    Acomment(String),
    Arule(Rule),
    Aset(Set),
}

fn parser(i: &str) -> nom::IResult<&str, Line> {
    alt((
        map(parse::comment, Acomment),
        map(parse::rule, Arule),
        map(parse::set, Aset),
    ))(i)
}

fn parse_clean(xs: Vec<String>) {
    let lines: Vec<Line> = xs
        .iter()
        .map(|l| (l, parser(&l)))
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
            Acomment(c) => println!("{}: {}", i, c),
            Arule(r) => println!("{}: {}", i, r),
            Aset(m) => println!("{}: {}", i, m),
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

    parse_clean(xs)
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

    parse_clean(xs)
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

    parse_clean(xs)
}
