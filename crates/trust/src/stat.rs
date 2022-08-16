/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fs::File;
use std::io::{BufReader, ErrorKind};
use std::time::UNIX_EPOCH;

use fapolicy_util::sha::sha256_digest;

use crate::error::Error;
use crate::error::Error::{FileIoError, MetaError};
use crate::Trust;

/// Actual delivers metadata about the actual file that exists on the filesystem.
/// This is used to identify discrepancies between the trusted and the actual files.
#[derive(PartialEq, Eq, Clone, Debug)]
pub struct Actual {
    pub size: u64,
    pub hash: String,
    pub last_modified: u64,
}

/// Trust status tag
#[derive(PartialEq, Eq, Clone, Debug)]
pub enum Status {
    /// Filesystem matches trust
    Trusted(Trust, Actual),
    /// Filesystem does not match trust
    Discrepancy(Trust, Actual),
    /// Does not exist on filesystem
    Missing(Trust),
}

/// check status of trust against the filesystem
pub fn check(t: &Trust) -> Result<Status, Error> {
    match File::open(&t.path) {
        Ok(f) => match collect_actual(&f) {
            Ok(act) if act.hash == t.hash && act.size == t.size => {
                Ok(Status::Trusted(t.clone(), act))
            }
            Ok(act) => Ok(Status::Discrepancy(t.clone(), act)),
            Err(e) => Err(e),
        },
        Err(e) if e.kind() == ErrorKind::NotFound => Ok(Status::Missing(t.clone())),
        Err(e) => Err(FileIoError(e)),
    }
}

fn collect_actual(file: &File) -> Result<Actual, Error> {
    let meta = file.metadata()?;
    let sha = sha256_digest(BufReader::new(file))?;
    Ok(Actual {
        size: meta.len(),
        hash: sha,
        last_modified: meta
            .modified()
            .map_err(|e| MetaError(format!("{}", e)))?
            .duration_since(UNIX_EPOCH)
            .map_err(|_| MetaError("failed to convert to epoch seconds".into()))?
            .as_secs(),
    })
}
