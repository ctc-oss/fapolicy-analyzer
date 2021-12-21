/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::io;
use thiserror::Error;

/// An Error that can occur in this crate
#[derive(Error, Debug)]
pub enum Error {
    #[error("error generating hash, {0}")]
    HashingError(#[from] io::Error),
}
