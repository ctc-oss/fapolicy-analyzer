/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::io;
use std::io::Read;

use thiserror::Error;

use data_encoding::HEXLOWER;
use ring::digest::{Context, SHA256};

#[derive(Error, Debug)]
pub enum Error {
    #[error("error generating hash, {0}")]
    HashingError(#[from] io::Error),
}

/// generate a sha256 hash as a string
pub fn sha256_digest<R: Read>(mut reader: R) -> Result<String, Error> {
    let mut context = Context::new(&SHA256);
    let mut buffer = [0; 1024];

    loop {
        let count = reader.read(&mut buffer)?;
        if count == 0 {
            break;
        }
        context.update(&buffer[..count]);
    }

    Ok(HEXLOWER.encode(context.finish().as_ref()))
}

// tested with integration tests
