use std::collections::HashMap;
use std::fs::File;
use std::io::{BufReader, prelude::*};
use std::iter::Iterator;
use std::str::FromStr;

use nom::alt;
use nom::character::complete::alpha1;
use nom::character::complete::line_ending as eol;
use nom::character::is_alphanumeric;
use nom::combinator::iterator;
use nom::named;
use nom::separated_pair;
use nom::sequence::terminated;
use nom::tag;
use nom::take_while;

pub struct LogObj {
    pub path: String,
    pub ftype: String,
}

impl LogObj {
    pub fn from_file(path: &str) -> Vec<LogObj> {
        let f = File::open(path).unwrap();
        let r = BufReader::new(f);

        r.lines()
            .map(|r| r.unwrap())
            .filter(|s| !s.is_empty() && !s.starts_with('#'))
            .map(|l| LogObj::from_str(&l).unwrap())
            .collect()
    }
}

fn is_valid_value_char(chr: char) -> bool {
    is_alphanumeric(chr as u8) || chr == '/' || chr == '-'
}

named!(end_of_line<&str, &str>, alt!(tag!(" ") | eol));
named!(alphanumericslash1<&str, &str>, take_while!(is_valid_value_char));
named!(kv_pair<&str, (&str, &str)>, separated_pair!(alpha1, nom::bytes::complete::tag("="), alphanumericslash1) );

impl FromStr for LogObj {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let clean = s.split(':').last().unwrap().trim_start();
        let mut it = iterator(clean, terminated(kv_pair, end_of_line));
        let map: HashMap<String, String> = it
            .map(|(k, v)| (String::from(k), String::from(v)))
            .collect();
        Ok(LogObj {
            path: map["path"].to_owned(),
            ftype: map["ftype"].to_owned(),
        })
    }
}
