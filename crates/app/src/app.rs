use crate::cfg::All;
use crate::cfg::PROJECT_NAME;
use crate::error::Error;
use directories::ProjectDirs;
use fapolicy_analyzer::users::{load_groups, load_users, Group, User};

use fapolicy_trust::db::DB;

use fapolicy_trust::ops::Changeset;
use fapolicy_trust::read::load_trust_db;
use serde::Deserialize;
use serde::Serialize;

/// Represents an immutable view of the application state.
/// Carries along the configuration that provided the state.
#[derive(Clone)]
pub struct State {
    pub config: All,
    pub trust_db: DB,
    pub users: Vec<User>,
    pub groups: Vec<Group>,
}

impl State {
    pub fn empty(cfg: &All) -> State {
        State {
            config: cfg.clone(),
            trust_db: DB::default(),
            users: vec![],
            groups: vec![],
        }
    }

    pub fn load(cfg: &All) -> Result<State, Error> {
        let trust_db = load_trust_db(&cfg.system.trust_db_path)?;
        Ok(State {
            config: cfg.clone(),
            trust_db,
            users: load_users(),
            groups: load_groups(),
        })
    }

    /// Apply a Changeset to this state, results in a new immutable state
    pub fn apply_trust_changes(&self, changes: Changeset) -> Self {
        println!("applying changeset to current state...");
        let modified = changes.apply(self.trust_db.clone());
        Self {
            config: self.config.clone(),
            trust_db: modified,
            users: self.users.clone(),
            groups: self.groups.clone(),
        }
    }
}

#[derive(Clone, Serialize, Deserialize)]
pub struct Config {
    pub data_dir: String,
}

impl Default for Config {
    fn default() -> Self {
        let proj_dirs =
            ProjectDirs::from("rs", "", PROJECT_NAME).expect("failed to init project dirs");

        let dd = proj_dirs.data_dir();

        Self {
            data_dir: dd.to_path_buf().into_os_string().into_string().unwrap(),
        }
    }
}
