/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::error::Error;
use crate::error::Error::MalformedFileMarker;
use crate::load::RuleFrom::{Disk, Mem};
use crate::parser::marker;
use crate::parser::parse::StrTrace;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::{fs, io};

pub(crate) type RuleSource = (PathBuf, String);

pub(crate) enum RuleFrom {
    Disk(PathBuf),
    Mem(String),
}

pub fn rules_from_disk(path: &str) -> Result<Vec<RuleSource>, Error> {
    rules_from(Disk(PathBuf::from(path)))
}

pub(crate) fn rules_from(src: RuleFrom) -> Result<Vec<RuleSource>, Error> {
    let r = match src {
        Disk(path) if path.is_dir() => rules_dir(&path)?,
        Disk(path) => rules_file(path)?,
        Mem(txt) => rules_text(txt)?,
    };
    Ok(r)
}

fn rules_file(path: PathBuf) -> Result<Vec<RuleSource>, io::Error> {
    let reader = File::open(&path).map(BufReader::new)?;
    let lines = reader
        .lines()
        .flatten()
        .map(|s| (path.clone(), s))
        .collect();
    Ok(lines)
}

pub fn read_sorted_d_files(from: &Path) -> Result<Vec<PathBuf>, io::Error> {
    let d_files: Result<Vec<PathBuf>, io::Error> =
        fs::read_dir(from)?.map(|e| e.map(|e| e.path())).collect();

    let mut d_files: Vec<PathBuf> = d_files?
        .into_iter()
        .filter(|p| p.is_file() && p.display().to_string().ends_with(".rules"))
        .collect();

    d_files.sort_by_key(|p| p.display().to_string());

    Ok(d_files)
}

fn rules_dir(rules_source_path: &Path) -> Result<Vec<RuleSource>, io::Error> {
    let d_files = read_sorted_d_files(rules_source_path)?;

    let d_files: Result<Vec<(PathBuf, File)>, io::Error> = d_files
        .into_iter()
        .map(|p| (p.clone(), File::open(&p)))
        .map(|(p, r)| r.map(|f| (p, f)))
        .collect();

    let d_files = d_files?.into_iter().map(|(p, f)| (p, BufReader::new(f)));

    // todo;; externalize result flattening via expect here
    let d_files = d_files.into_iter().map(|(path, rdr)| {
        (
            path.clone(),
            rdr.lines()
                .collect::<Result<Vec<String>, io::Error>>()
                .unwrap_or_else(|_| {
                    panic!("failed to read lines from rules file, {}", path.display())
                }),
        )
    });

    let d_files: Vec<RuleSource> = d_files
        .into_iter()
        .flat_map(|(src, lines)| {
            lines
                .iter()
                .map(|l| (src.clone(), l.clone()))
                .collect::<Vec<RuleSource>>()
        })
        .collect();

    // todo;; revisit result flattening
    Ok(d_files)
}

fn rules_text(rules_text: String) -> Result<Vec<RuleSource>, Error> {
    let mut origin: Option<PathBuf> = Some(PathBuf::from("00-analyzer.rules"));
    let mut lines = vec![];
    for (num, line) in rules_text.split('\n').map(|s| s.trim()).enumerate() {
        match marker::parse(StrTrace::new(line)) {
            Ok((_, v)) => origin = Some(v),
            Err(_) if line.starts_with('[') || line.ends_with(']') => {
                // todo;; could improve the introspection of the parse error here to improve
                //        the trace that is reported; the marker parser could also be reviewed
                return Err(MalformedFileMarker(num + 1, line.trim().to_string()));
            }
            Err(_) => {
                let r = origin
                    .as_ref()
                    .map(|p| (p.clone(), line.to_string()))
                    .map(RuleSource::from)
                    .unwrap();
                lines.push(r);
            }
        };
    }

    // todo;; split the
    Ok(lines)
}

#[cfg(test)]
mod test {
    use crate::error;
    use crate::load::rules_text;
    use std::collections::HashMap;
    use std::path::PathBuf;

    fn to_map(txt: &str) -> Result<HashMap<PathBuf, Vec<String>>, error::Error> {
        let mut mapped: HashMap<PathBuf, Vec<String>> = HashMap::new();
        for (p, r) in rules_text(txt.to_string())? {
            if !mapped.contains_key(&p) {
                mapped.insert(p.clone(), vec![]);
            }
            mapped.get_mut(&p).unwrap().push(r.clone());
        }
        Ok(mapped)
    }

    #[test]
    fn text_single() -> Result<(), error::Error> {
        let txt = r#"
        [foo.rules]
        allow perm=any all : all"#;
        let r = to_map(txt)?;
        assert!(r.contains_key(&PathBuf::from("foo.rules")));
        Ok(())
    }

    #[test]
    fn text_multi_file() -> Result<(), error::Error> {
        let txt = r#"
        [foo.rules]
        allow perm=any all : all
        [bar.rules]
        allow perm=any all : all"#;
        let r = to_map(txt)?;
        assert!(r.contains_key(&PathBuf::from("foo.rules")));
        assert!(r.contains_key(&PathBuf::from("bar.rules")));
        Ok(())
    }

    #[test]
    fn text_empty_file() -> Result<(), error::Error> {
        let txt = r#"
        [foo.rules]
        [bar.rules]
        allow perm=any all : all"#;
        let r = to_map(txt)?;
        assert!(!r.contains_key(&PathBuf::from("foo.rules")));
        assert!(r.contains_key(&PathBuf::from("bar.rules")));
        Ok(())
    }
}
