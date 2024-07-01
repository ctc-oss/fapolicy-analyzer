/*
 * Copyright Concurrent Technologies Corporation 2024
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::filter::db::DB;
use crate::filter::error::Error;
use crate::filter::read;

pub fn file(path: &str) -> Result<DB, Error> {
    read::file(path.into())
}

pub fn mem(txt: &str) -> Result<DB, Error> {
    read::mem(txt)
}

pub fn with_error_message(txt: &str) -> Result<DB, String> {
    mem(txt).map_err(|e| e.to_string())
}
