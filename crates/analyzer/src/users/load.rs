use std::fs::File;
use std::io::{BufRead, BufReader};

use crate::users::{parse, Group, User};

pub fn users() -> Vec<User> {
    let lines = lines_from("/etc/passwd");
    lines
        .iter()
        .flat_map(|s| parse::user(s))
        .map(|v| v.1)
        .collect()
}

pub fn groups() -> Vec<Group> {
    let lines: Vec<String> = lines_from("/etc/group");
    lines
        .iter()
        .flat_map(|s| parse::group(s))
        .map(|v| v.1)
        .collect()
}

fn lines_from(path: &str) -> Vec<String> {
    let f = File::open(path).expect("failed to open file");
    let buff = BufReader::new(f);

    buff.lines()
        .map(|r| r.unwrap())
        .filter(|s| !s.is_empty() && !s.starts_with('#'))
        .collect()
}
