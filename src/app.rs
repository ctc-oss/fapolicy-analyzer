use serde::Deserialize;
use serde::Serialize;

use crate::api::Trust;
use crate::sys::Config;
use crate::trust::load_trust_db;
use crate::trust::Changeset;

#[derive(Clone, Serialize, Deserialize)]
pub struct State {
    pub config: Config,
    pub trust_db: Vec<Trust>,
}

impl State {
    pub fn new(cfg: &Config) -> State {
        State {
            config: cfg.clone(),
            trust_db: load_trust_db(&cfg.trust_db_path),
        }
    }

    pub fn apply_trust_changes(&self, _changes: Changeset) -> Self {
        // todo;; apply changeset
        println!("applying changeset to current state...");
        let updated_db = self.trust_db.clone();

        Self {
            config: self.config.clone(),
            trust_db: updated_db,
        }
    }
}
