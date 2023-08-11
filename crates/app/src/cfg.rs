/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use confy::ConfyError;
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
        let conf_file = All::config_file()?;
        confy::load_path(conf_file).map_err(ConfigError)
    }

    pub fn config_file() -> Result<PathBuf, Error> {
        let mut config = PathBuf::from(config_dir());
        config.push("config.toml");
        Ok(config)
    }

    pub fn data_dir(&self) -> &str {
        self.application.data_dir.as_str()
    }
}

#[cfg(not(feature = "xdg"))]
pub fn data_dir() -> String {
    format!("/var/lib/{}", PROJECT_NAME)
}

#[cfg(feature = "xdg")]
pub fn data_dir() -> String {
    let proj_dirs = directories::ProjectDirs::from("rs", "", PROJECT_NAME)
        .expect("failed to init project dirs");
    let dd = proj_dirs.data_dir();
    dd.to_path_buf().into_os_string().into_string().unwrap()
}

#[cfg(not(feature = "xdg"))]
pub fn config_dir() -> String {
    format!("/etc/{}", PROJECT_NAME)
}

#[cfg(feature = "xdg")]
pub fn config_dir() -> String {
    let proj_dirs = directories::ProjectDirs::from("rs", "", PROJECT_NAME)
        .expect("failed to init project dirs");
    let dd = proj_dirs.config_dir();
    dd.to_path_buf().into_os_string().into_string().unwrap()
}

#[cfg(not(feature = "xdg"))]
pub fn log_dir() -> String {
    format!("/var/log/{}", PROJECT_NAME)
}

#[cfg(feature = "xdg")]
pub fn log_dir() -> String {
    let proj_dirs = directories::ProjectDirs::from("rs", "", PROJECT_NAME)
        .expect("failed to init project dirs");
    let dd = proj_dirs.state_dir().unwrap();
    dd.to_path_buf().into_os_string().into_string().unwrap()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn check_config_dir() {
        let path = All::config_file().expect("conf path");
        assert!(path.ends_with(format!(".config/{}/config.toml", PROJECT_NAME)));
    }
}
