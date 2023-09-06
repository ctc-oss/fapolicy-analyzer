/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use nom::error::{ErrorKind, ParseError};
use thiserror::Error;

#[derive(Error, Clone, Debug)]
pub enum Error {
    #[error("General config error")]
    General,

    #[error("Config entry should be lhs=rhs")]
    MalformedConfig,

    #[error("{0} is an unknown lhs value")]
    InvalidLhs(String),

    #[error("Expected rhs to be of type")]
    InvalidRhs,

    #[error("Expected data: {0}")]
    Unexpected(String),

    #[error("Expected 0 or 1")]
    ExpectedBool,

    #[error("Expected positive number")]
    ExpectedNumber,

    #[error("Expected string")]
    ExpectedString,

    #[error("Expected string list")]
    ExpectedStringList,

    #[error("Expected trust backend list (rpm, file, deb)")]
    ExpectedTrustBackendList,

    #[error("Expected integrity source (none, size, hash)")]
    ExpectedIntegritySource,

    #[error("Unknown trust backend {0}")]
    UnknownTrustBackend(String),
}

impl<I> ParseError<I> for Error {
    fn from_error_kind(_: I, _: ErrorKind) -> Self {
        Error::General
    }

    fn append(_: I, _: ErrorKind, other: Self) -> Self {
        other
    }
}
