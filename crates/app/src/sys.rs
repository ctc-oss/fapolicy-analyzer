use std::fs::File;
use std::io::Write;

use serde::Deserialize;
use serde::Serialize;
use thiserror::Error;

use crate::app::State;
use crate::sys::Error::{DaemonError, WriteAncillaryFail};
use fapolicy_daemon::fapolicyd::{RPM_DB_PATH, TRUST_DB_PATH, TRUST_FILE_PATH};

#[derive(Error, Debug)]
pub enum Error {
    #[error("{0}")]
    WriteAncillaryFail(String),
    #[error("{0}")]
    DaemonError(#[from] fapolicy_daemon::error::Error),
}

pub fn deploy_app_state(state: &State) -> Result<(), Error> {
    let mut tf = File::create(&state.config.system.ancillary_trust_path)
        .map_err(|_| WriteAncillaryFail("unable to create ancillary trust".to_string()))?;
    for (path, meta) in state.trust_db.iter() {
        if meta.is_ancillary() {
            tf.write_all(
                format!(
                    "{} {} {}\n",
                    path,
                    meta.trusted.size.to_string(),
                    meta.trusted.hash
                )
                .as_bytes(),
            )
            .map_err(|_| WriteAncillaryFail("unable to write ancillary trust entry".to_string()))?;
        }
    }
    fapolicy_daemon::reload_databases().map_err(DaemonError)
}

/// host system configuration information
/// generally loaded from the XDG user configuration
#[derive(Clone, Serialize, Deserialize)]
pub struct Config {
    pub trust_db_path: String,
    pub system_trust_path: String,
    pub ancillary_trust_path: String,
}

impl ::std::default::Default for Config {
    fn default() -> Self {
        Self {
            trust_db_path: TRUST_DB_PATH.to_string(),
            system_trust_path: RPM_DB_PATH.to_string(),
            ancillary_trust_path: TRUST_FILE_PATH.to_string(),
        }
    }
}
