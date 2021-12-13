/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fmt::{Display, Formatter};

use serde::Deserialize;
use serde::Serialize;

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum TrustSource {
    Ancillary,
    System,
}

impl Display for TrustSource {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        match *self {
            TrustSource::Ancillary => write!(f, "Ancillary"),
            TrustSource::System => write!(f, "System"),
        }
    }
}
