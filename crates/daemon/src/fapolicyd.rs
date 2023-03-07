/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

// todo;; tracking the fapolicyd specific bits in here to determine if bindings are worthwhile

use crate::error::Error;
use std::fs::File;
use std::io::Read;
use std::path::Path;
use std::thread;
use std::time::Duration;

pub const TRUST_LMDB_PATH: &str = "/var/lib/fapolicyd";
pub const TRUST_LMDB_NAME: &str = "trust.db";
pub const TRUST_DIR_PATH: &str = "/etc/fapolicyd/trust.d";
pub const TRUST_FILE_PATH: &str = "/etc/fapolicyd/fapolicyd.trust";
pub const RULES_FILE_PATH: &str = "/etc/fapolicyd/rules.d";
pub const COMPILED_RULES_PATH: &str = "/etc/fapolicyd/compiled.rules";
pub const RPM_DB_PATH: &str = "/var/lib/rpm";
pub const FIFO_PIPE: &str = "/run/fapolicyd/fapolicyd.fifo";

#[derive(Clone, Debug)]
pub enum Version {
    Unknown,
    Release { major: u8, minor: u8, patch: u8 },
}

/// watch a fapolicyd log at the specified path for the
/// message it prints when ready to start polling events
pub fn wait_until_ready(path: &Path) -> Result<(), Error> {
    let mut f = File::open(path)?;
    for _ in 0..10 {
        thread::sleep(Duration::from_secs(1));
        let mut s = String::new();
        f.read_to_string(&mut s)?;
        if s.contains("Starting to listen for events") {
            return Ok(());
        }
    }
    Err(Error::NotReady)
}
