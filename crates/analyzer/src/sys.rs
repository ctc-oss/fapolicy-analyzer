use std::fs::File;
use std::io::Write;

use serde::Deserialize;
use serde::Serialize;
use thiserror::Error;

use crate::app::State;
use crate::fapolicyd;
use crate::sys::Error::WriteAncillaryFail;
use fapolicy_trust::trust::TrustSource::Ancillary;

#[derive(Error, Debug)]
pub enum Error {
    #[error("{0}")]
    WriteAncillaryFail(String),
    #[error("{0}")]
    FapolicydReloadFail(String),
}

pub fn deploy_app_state(state: &State) -> Result<(), Error> {
    let mut tf = File::create(&state.config.system.ancillary_trust_path)
        .map_err(|_| WriteAncillaryFail("unable to create ancillary trust".to_string()))?;
    for t in &state.trust_db {
        if t.source == Ancillary {
            tf.write_all(format!("{} {} {}\n", t.path, t.size.to_string(), t.hash).as_bytes())
                .map_err(|_| {
                    WriteAncillaryFail("unable to write ancillary trust entry".to_string())
                })?;
        }
    }
    fapolicyd::reload_databases()
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
            trust_db_path: fapolicyd::TRUST_DB_PATH.to_string(),
            system_trust_path: fapolicyd::RPM_DB_PATH.to_string(),
            ancillary_trust_path: fapolicyd::TRUST_FILE_PATH.to_string(),
        }
    }
}
