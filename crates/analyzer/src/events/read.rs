/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fs::File;
use std::io;
use std::io::{BufRead, BufReader};

use crate::error::Error;
use crate::events::event::Event;
use crate::events::parse::parse_event;

pub fn from_file(path: &str) -> Result<Vec<Event>, Error> {
    let buff = BufReader::new(File::open(path)?);
    let lines: Result<Vec<String>, io::Error> = buff.lines().collect();
    Ok(lines?
        .iter()
        .filter(|s| !s.is_empty() && !s.starts_with('#'))
        .map(|l| parse_event(&l).unwrap().1)
        .collect())
}

pub fn from_syslog(path: &str) -> Result<Vec<Event>, Error> {
    let buff = BufReader::new(File::open(path)?);
    let lines: Result<Vec<String>, io::Error> = buff.lines().collect();
    Ok(lines?
        .iter()
        .filter(|s| s.contains("fapolicyd") && s.contains("rule="))
        .flat_map(|l| parse_event(l.as_str()))
        .map(|(_, e)| e.clone())
        .collect())
}
