/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::string::FromUtf8Error;
use thiserror::Error;

// errors that can occur in this crate
#[derive(Error, Debug)]
pub enum Error {
    #[error("{0}")]
    FapolicydReloadFail(String),

    #[error("dbus {0}")]
    DbusFailure(#[from] dbus::Error),

    #[error("dbus method-call {0}")]
    DbusMethodCall(String),

    #[error("{0}")]
    ServiceCheckFailure(String),
}
