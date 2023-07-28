use std::fs::File;
use std::io;
use std::io::{BufRead, BufReader};
use std::path::PathBuf;

pub(crate) type RuleSource = (PathBuf, String);

pub(crate) enum RuleFrom {
    Disk(PathBuf),
    Mem(String),
}

fn conf_file(path: PathBuf) -> Result<Vec<RuleSource>, io::Error> {
    let reader = File::open(&path).map(BufReader::new)?;
    let lines = reader
        .lines()
        .flatten()
        .map(|s| (path.clone(), s))
        .collect();
    Ok(lines)
}
