use crate::filter::error::Error;
use crate::filter::{Line, DB};
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::PathBuf;

pub fn file(path: &str) -> Result<DB, Error> {
    let reader = File::open(path)
        .map(BufReader::new)
        .map_err(|_| Error::General("Parse file".to_owned()))?;
    lines(reader.lines().flatten().collect())
}

pub fn mem(txt: &str) -> Result<DB, Error> {
    lines(txt.split('\n').map(|s| s.to_string()).collect())
}

fn lines(src: Vec<String>) -> Result<DB, Error> {
    let mut lines = vec![];
    let mut skip_blank = true;

    for s in src {
        let s = s.trim_end();
        if s.is_empty() {
            if skip_blank {
                continue;
            }
            lines.push(Line::BlankLine);
            skip_blank = true;
        } else if s.trim_start().starts_with('#') {
            lines.push(Line::Comment(s.to_string()));
            skip_blank = false;
        } else {
            lines.push(Line::Valid(s.to_owned()));
            skip_blank = false;
        }
    }
    Ok(lines.into())
}
