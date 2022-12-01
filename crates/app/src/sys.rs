/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::io;
use std::path::{Path, PathBuf};

use serde::Deserialize;
use serde::Serialize;
use thiserror::Error;

use fapolicy_daemon::fapolicyd::{
    RPM_DB_PATH, RULES_FILE_PATH, TRUST_DIR_PATH, TRUST_FILE_PATH, TRUST_LMDB_PATH,
};

use crate::app::State;
use crate::sys::Error::{WriteAncillaryFail, WriteRulesFail};

#[derive(Error, Debug)]
pub enum Error {
    #[error("Failed to write trust; {0}")]
    WriteAncillaryFail(io::Error),
    #[error("Failed to write rules; {0}")]
    WriteRulesFail(io::Error),
    #[error("{0}")]
    DaemonError(#[from] fapolicy_daemon::error::Error),
}

pub fn deploy_app_state(state: &State) -> Result<(), Error> {
    // write rules model
    fapolicy_rules::write::db(
        &state.rules_db,
        &PathBuf::from(&state.config.system.rules_file_path),
    )
    .map_err(WriteRulesFail)?;

    // write file trust db
    fapolicy_trust::write::file_trust(
        &state.trust_db,
        PathBuf::from(&state.config.system.trust_dir_path),
    )
    .map_err(WriteAncillaryFail)?;

    Ok(())
}

/// default path for the syslog log file in RH environments
const RHEL_SYSLOG_LOG_FILE_PATH: &str = "/var/log/messages";

/// host system configuration information
/// generally loaded from the XDG user configuration
#[derive(Clone, Serialize, Deserialize)]
pub struct Config {
    // rules.d path
    #[serde(default = "rules_file_path")]
    pub rules_file_path: String,

    // lmdb directory path
    #[serde(default = "trust_lmdb_path")]
    pub trust_lmdb_path: String,

    // rpmdb path
    #[serde(default = "system_trust_path")]
    pub system_trust_path: String,

    // trust.d path
    #[serde(default = "trust_dir_path")]
    pub trust_dir_path: String,

    // fapolicyd.trust path
    #[serde(default = "trust_file_path")]
    pub trust_file_path: String,

    // syslog messages file path
    #[serde(default = "syslog_file_path")]
    pub syslog_file_path: String,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            trust_lmdb_path: TRUST_LMDB_PATH.to_string(),
            rules_file_path: RULES_FILE_PATH.to_string(),
            system_trust_path: RPM_DB_PATH.to_string(),
            trust_dir_path: TRUST_DIR_PATH.to_string(),
            trust_file_path: TRUST_FILE_PATH.to_string(),
            syslog_file_path: RHEL_SYSLOG_LOG_FILE_PATH.to_string(),
        }
    }
}

//
// private helpers for serde
//

fn trust_lmdb_path() -> String {
    TRUST_LMDB_PATH.into()
}

fn rules_file_path() -> String {
    RULES_FILE_PATH.into()
}

fn system_trust_path() -> String {
    RPM_DB_PATH.into()
}

fn trust_dir_path() -> String {
    TRUST_DIR_PATH.into()
}

fn trust_file_path() -> String {
    TRUST_FILE_PATH.into()
}

fn syslog_file_path() -> String {
    RHEL_SYSLOG_LOG_FILE_PATH.into()
}
