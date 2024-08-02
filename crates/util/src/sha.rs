/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use digest::Digest;
use sha2::Sha256;
use std::io;
use std::io::Read;

use thiserror::Error;

#[derive(Error, Debug)]
pub enum Error {
    #[error("error generating hash, {0}")]
    HashingError(#[from] io::Error),
}

/// generate a sha256 hash as a string
pub fn sha256_digest<R: Read>(mut src: R) -> Result<String, Error> {
    let mut hasher = Sha256::new();
    io::copy(&mut src, &mut hasher)?;
    let hash = hasher.finalize();
    Ok(format!("{:x}", hash))
}

// tested with integration tests
