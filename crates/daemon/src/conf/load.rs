use std::fs::File;
use std::io;
use std::io::{BufRead, BufReader};
use std::path::PathBuf;

pub(crate) enum RuleFrom {
    Disk(PathBuf),
    Mem(String),
}

fn conf_file(path: PathBuf) -> Result<Vec<String>, io::Error> {
    let reader = File::open(&path).map(BufReader::new)?;
    let lines = reader.lines().flatten().collect();
    Ok(lines)
}
