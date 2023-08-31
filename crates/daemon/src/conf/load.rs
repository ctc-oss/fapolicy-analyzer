/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::conf::error::Error;
use crate::conf::read;
use crate::Config;

pub fn config(path: &str) -> Result<Config, Error> {
    read::file(path.into())
}
