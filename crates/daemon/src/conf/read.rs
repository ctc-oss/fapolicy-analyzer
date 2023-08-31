/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::conf::error::Error;
use crate::conf::parse;
use crate::Config;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::PathBuf;

fn lines(path: PathBuf) -> Result<Vec<String>, Error> {
    let reader = File::open(path)
        .map(BufReader::new)
        .map_err(|_| Error::General)?;
    let lines = reader.lines().flatten().collect();
    Ok(lines)
}

pub fn file(path: PathBuf) -> Result<Config, Error> {
    let mut config = Config::empty();
    for s in lines(path)? {
        if s.trim().is_empty() || s.trim_start().starts_with('#') {
            continue;
        }

        match parse::token(&s) {
            Ok(v) => config.apply_ok(v),
            Err((k, v, _)) => config.apply_err(k, v),
        };
    }
    Ok(config)
}
