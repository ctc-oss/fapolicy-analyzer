use fapolicy_analyzer::rules::Rule;
use std::fs::File;
use std::io::{BufRead, BufReader};

pub fn parser(i: &str) -> nom::IResult<&str, Rule> {
    fapolicy_analyzer::rules::parse::rule(i)
}

#[test]
fn test_parse_clean() {
    let f = File::open("tests/data/rules.txt").expect("failed to open file");
    let buff = BufReader::new(f);

    let xs: Vec<String> = buff
        .lines()
        .map(|r| r.unwrap())
        .filter(|s| !s.is_empty() && !s.starts_with('#'))
        .collect();

    let rules: Vec<Rule> = xs
        .iter()
        .map(|l| (l, parser(&l)))
        .flat_map(|(l, r)| match r {
            Ok((_, rule)) => Some(rule),
            Err(_) => {
                println!("[fail] {}", l);
                None
            }
        })
        .collect();

    for (i, rule) in rules.iter().enumerate() {
        println!("{}: {}", i, rule);
    }

    println!(
        "{}/{} - {:.2}%",
        rules.len(),
        xs.len(),
        rules.len() as f32 / xs.len() as f32
    );

    // assert_eq!(17, y.len());
}
