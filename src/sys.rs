use serde::Deserialize;
use serde::Serialize;

use crate::app::State;
use crate::fapolicyd;

pub fn deploy_app_state(_state: &State) {
    // todo;; back up trust file
    println!("backing up trust file...");

    // todo;; write changeset
    println!("writing changeset to disk...");

    // todo;; signal fapolicyd update
    println!("signaling fapolicdy reload...");

    // todo;; return new Application
    println!("reloading app trust database...");
}

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
            system_trust_path: fapolicyd::TRUST_FILE_PATH.to_string(),
            ancillary_trust_path: fapolicyd::RPM_DB_PATH.to_string(),
        }
    }
}
