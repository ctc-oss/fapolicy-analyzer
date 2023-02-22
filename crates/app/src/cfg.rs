/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use confy::ConfyError;
use directories::ProjectDirs;
use serde::Deserialize;
use serde::Serialize;
use std::path::PathBuf;

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
        confy::load(PROJECT_NAME).map_err(ConfigError)
    }

    pub fn config_dir() -> Result<PathBuf, Error> {
        // the arguments here match the confy::load impl
        ProjectDirs::from("rs", "", PROJECT_NAME)
            .ok_or(ConfigError(ConfyError::BadConfigDirectoryStr))
            .map(|d| d.config_dir().to_path_buf())
    }

    pub fn data_dir(&self) -> &str {
        self.application.data_dir.as_str()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn check_config_dir() {
        let path = All::config_dir().expect("conf path");
        assert!(path.ends_with(format!(".config/{}", PROJECT_NAME)));
    }
}
