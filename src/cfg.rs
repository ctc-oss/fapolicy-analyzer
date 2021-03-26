use serde::Deserialize;
use serde::Serialize;

use crate::fapolicyd;

#[derive(Clone, Serialize, Deserialize)]
pub struct ApplicationCfg {
    pub system: SystemCfg,
}

impl ::std::default::Default for ApplicationCfg {
    fn default() -> Self {
        Self {
            system: Default::default(),
        }
    }
}

#[derive(Clone, Serialize, Deserialize)]
pub struct SystemCfg {
    pub trust_db_path: String,
    pub system_trust_path: String,
    pub ancillary_trust_path: String,
}

impl ::std::default::Default for SystemCfg {
    fn default() -> Self {
        Self {
            trust_db_path: fapolicyd::TRUST_DB_PATH.to_string(),
            system_trust_path: fapolicyd::TRUST_FILE_PATH.to_string(),
            ancillary_trust_path: fapolicyd::RPM_DB_PATH.to_string(),
        }
    }
}

pub fn load() -> ApplicationCfg {
    confy::load("fapolicy-analyzer").expect("unable to load user configuration")
}
