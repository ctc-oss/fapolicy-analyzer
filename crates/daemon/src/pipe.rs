/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::error::Error;
use crate::fapolicyd::FIFO_PIPE;
use crate::pipe::Commands::{FlushCache, ReloadRules, ReloadTrust};
use std::io::Write;

#[repr(u8)]
enum Commands {
    ReloadTrust = 1,
    FlushCache = 2,
    ReloadRules = 3,
}

type CmdResult = Result<(), Error>;

// 3
pub fn reload_rules() -> CmdResult {
    ReloadRules.send()
}

// 2
pub fn flush_cache() -> CmdResult {
    FlushCache.send()
}

// 1
pub fn reload_trust() -> CmdResult {
    ReloadTrust.send()
}

impl Commands {
    fn send(self) -> CmdResult {
        let mut fifo = std::fs::OpenOptions::new()
            .write(true)
            .read(false)
            .open(FIFO_PIPE)?;

        // the new line char is required here
        fifo.write_all(format!("{}\n", self as u8).as_bytes())?;

        Ok(())
    }
}
