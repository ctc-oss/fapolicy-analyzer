use serde::Deserialize;
use serde::Serialize;

use crate::api::TrustSource;
use crate::app::State;
use crate::fapolicyd;
use std::fs::File;
use std::io::Write;

pub fn deploy_app_state(state: &State) -> Result<(), String> {
    // todo;; back up trust file
    println!("backing up trust file...");

    println!("writing changeset to disk...");
    let mut tf = File::create(&state.config.system.ancillary_trust_path)
        .expect("unable to create ancillary trust");
    for t in &state.trust_db {
        if t.source == TrustSource::Ancillary {
            tf.write_all(format!("{} {} {}\n", t.path, t.size.to_string(), t.hash).as_bytes())
                .expect("unable to write ancillary trust file")
        }
    }

    println!("signaling fapolicdy reload...");
    fapolicyd::reload_databases();

    Ok(())
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
