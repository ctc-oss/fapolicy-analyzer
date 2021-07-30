use std::fs::File;
use std::io::{prelude::*, BufReader};
use std::iter::Iterator;
use std::str::FromStr;

use nom::bytes::complete::tag;
use nom::character::complete::space0;
use nom::character::complete::{digit1, space1};
use nom::sequence::{preceded, terminated};

use crate::rules::*;

#[derive(Debug)]
pub struct Event {
    pub rule_id: i32,
    pub dec: Decision,
    pub perm: Permission,
    pub auid: i32,
    pub pid: i32,
    pub subj: Subject,
    pub obj: Object,
}

impl FromStr for Event {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match parse_event(s) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Event from string".into()),
        }
    }
}

pub fn parse_event(i: &str) -> nom::IResult<&str, Event> {
    match nom::combinator::complete(nom::sequence::tuple((
        terminated(preceded(tag("rule="), digit1), space1),
        terminated(preceded(tag("dec="), parse::decision), space1),
        terminated(parse::permission, space1),
        terminated(preceded(tag("auid="), digit1), space1),
        terminated(preceded(tag("pid="), digit1), space1),
        terminated(parse::subject, space1),
        terminated(tag(":"), space0),
        parse::object,
    )))(i)
    {
        Ok((remaining_input, (id, dec, perm, auid, pid, subj, _, obj))) => Ok((
            remaining_input,
            Event {
                rule_id: id.parse().unwrap(),
                dec,
                perm,
                auid: auid.parse().unwrap(),
                pid: pid.parse().unwrap(),
                subj,
                obj,
            },
        )),
        Err(e) => {
            println!("foo");
            Err(e)
        }
    }
}

impl Event {
    pub fn from_file(path: &str) -> Vec<Event> {
        let f = File::open(path).unwrap();
        let r = BufReader::new(f);

        r.lines()
            .map(|r| r.unwrap())
            .filter(|s| !s.is_empty() && !s.starts_with('#'))
            .map(|l| parse_event(&l).unwrap().1)
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_log_event() {
        let e = "rule=9 dec=allow perm=execute auid=1003 pid=5555 exe=/usr/bin/bash : path=/usr/bin/vi ftype=application/x-executable";
        let (rem, e) = parse_event(e).ok().unwrap();
        assert_eq!(9, e.rule_id);
        assert!(rem.is_empty());
        assert_eq!(e.dec, Decision::Allow);
        assert_eq!(e.perm, Permission::Execute);
        assert_eq!(e.auid, 1003);
        assert_eq!(e.pid, 5555);
    }
}
