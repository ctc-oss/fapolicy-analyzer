/*
 * Copyright Concurrent Technologies Corporation 2024
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::filter::db::DB;
use crate::filter::error::Error;

pub fn mem(txt: &str) -> Result<DB, Error> {
    Ok(DB)
}
