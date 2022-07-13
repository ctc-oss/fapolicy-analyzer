/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::io;

use thiserror::Error;

#[derive(Error, Debug)]
pub enum Error {
    #[error("File IO Error: {0}")]
    FileIoError(#[from] io::Error),

    #[error("Malformed marker @ {0}: {1}")]
    MalformedFileMarker(usize, String),
}
