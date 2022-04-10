/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::PathBuf;
use std::{fs, io};

pub(crate) type RuleSource = (PathBuf, String);

pub fn rules_from(path: PathBuf) -> Result<Vec<RuleSource>, io::Error> {
    if path.is_dir() {
        rules_dir(path)
    } else {
        rules_file(path)
    }
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

fn rules_dir(rules_source_path: PathBuf) -> Result<Vec<RuleSource>, io::Error> {
    let d_files: Result<Vec<PathBuf>, io::Error> = fs::read_dir(&rules_source_path)?
        .map(|e| e.map(|e| e.path()))
        .collect();

    let mut d_files: Vec<PathBuf> = d_files?
        .into_iter()
        .filter(|p| p.is_file() && p.display().to_string().ends_with(".rules"))
        .collect();
    d_files.sort_by_key(|p| p.display().to_string());

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
