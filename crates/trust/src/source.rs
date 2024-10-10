/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fmt::{Display, Formatter};
use std::path::PathBuf;

use serde::Deserialize;
use serde::Serialize;

/// Internal structure used during parsing
pub(crate) type TrustSourceEntry = (PathBuf, String);

/// Identifies the origin of the trust entry
/// System = RPM
/// Ancillary = fapolicyd.trust
/// DFile = trust.d
/// todo;; deb
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum TrustSource {
    System,
    Ancillary,
    DFile(String),
}

impl Display for TrustSource {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        match *self {
            TrustSource::Ancillary => write!(f, "Ancillary"),
            TrustSource::DFile(_) => write!(f, "Ancillary"),
            TrustSource::System => write!(f, "System"),
        }
    }
}
