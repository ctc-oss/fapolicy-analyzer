/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use serde::Deserialize;
use serde::Serialize;

use crate::error::Error;
use crate::error::Error::ConfigError;
use crate::{app, sys};

pub const PROJECT_NAME: &str = "fapolicy-analyzer";

/// All configuration loaded from the user toml under XDG config dir
#[derive(Clone, Serialize, Deserialize, Default)]
pub struct All {
    pub system: sys::Config,
    pub application: app::Config,
}

impl All {
    pub fn load() -> Result<All, Error> {
        confy::load(PROJECT_NAME, None).map_err(ConfigError)
    }

    pub fn data_dir(&self) -> &str {
        self.application.data_dir.as_str()
    }
}
