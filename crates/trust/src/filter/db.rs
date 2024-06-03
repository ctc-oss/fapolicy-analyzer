/*
 * Copyright Concurrent Technologies Corporation 2024
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::filter::error::Error;

#[derive(Clone, Debug, Default)]
pub struct DB;

impl DB {
    pub fn from_file(path: &str) -> Result<DB, Error> {
        Ok(DB)
    }
}
