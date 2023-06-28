/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::time::SystemTimeError;
use thiserror::Error;

/// An error that can occur
#[derive(Error, Debug)]
pub enum Error {
    #[error("General failure: {0}")]
    GeneralFail(String),

    #[error("{0}")]
    DurationError(#[from] SystemTimeError),

    #[error("Failed to init auparse")]
    NativeInitFail,

    #[error("Native error {0}")]
    AuditParseError(#[from] auparse_sys::error::Error),
}
