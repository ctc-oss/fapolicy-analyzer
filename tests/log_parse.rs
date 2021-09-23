use fapolicy_analyzer::event::Event;
use fapolicy_analyzer::log;
use nom::combinator::map;
use std::fs::File;
use std::io::{BufRead, BufReader};

enum Line {
    AnEvent(Event),
}

fn parser(i: &str) -> nom::IResult<&str, Line> {
    map(log::parse_event, Line::AnEvent)(i)
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
            Line::AnEvent(c) => println!("{}: {:?}", i, c),
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
fn test_parse_clean_1() {
    let f = File::open("tests/data/full.log").expect("failed to open file");
    let buff = BufReader::new(f);

    let xs: Vec<String> = buff
        .lines()
        .map(|r| r.unwrap())
        .filter(|s| s.starts_with("rule="))
        .collect();

    parse_lines(xs)
}
