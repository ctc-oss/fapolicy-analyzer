/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::conf;
use crate::conf::db::Line;
use crate::conf::error::Error;
use crate::conf::parse;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::PathBuf;

fn lines_in_file(path: PathBuf) -> Result<Vec<String>, Error> {
    let reader = File::open(path)
        .map(BufReader::new)
        .map_err(|_| Error::General)?;
    let lines = reader.lines().flatten().collect();
    Ok(lines)
}

pub fn file(path: PathBuf) -> Result<conf::db::DB, Error> {
    let mut lines = vec![];
    let mut skip_blank = true;

    for s in lines_in_file(path)? {
        let s = s.trim();
        if s.is_empty() {
            if skip_blank {
                continue;
            }
            lines.push(Line::BlankLine);
            skip_blank = true;
        } else if s.starts_with('#') {
            lines.push(Line::Comment(s.to_string()));
            skip_blank = false;
        } else {
            match parse::token(s) {
                Ok(v) => lines.push(Line::Valid(v)),
                Err((lhs, rhs, Error::InvalidLhs(_))) => {
                    lines.push(Line::Invalid(format!("{lhs}={rhs}")))
                }
                Err((v, _, Error::MalformedConfig)) => lines.push(Line::Invalid(v.to_string())),
                Err((lhs, rhs, _)) => lines.push(Line::Invalid(format!("{lhs}={rhs}"))),
            };
            skip_blank = false;
        }
    }
    Ok(lines.into())
}
