use directories::ProjectDirs;
use serde::Deserialize;
use serde::Serialize;

use fapolicy_analyzer::rules::db::DB as RulesDB;
use fapolicy_analyzer::rules::read::load_rules_db;
use fapolicy_analyzer::users::{load_groups, load_users, Group, User};
use fapolicy_trust::db::DB as TrustDB;
use fapolicy_trust::ops::Changeset;
use fapolicy_trust::read::{check_trust_db, load_trust_db};

use crate::cfg::All;
use crate::cfg::PROJECT_NAME;
use crate::error::Error;

/// Represents an immutable view of the application state.
/// Carries along the configuration that provided the state.
#[derive(Clone)]
pub struct State {
    pub config: All,
    pub trust_db: TrustDB,
    pub rules_db: RulesDB,
    pub users: Vec<User>,
    pub groups: Vec<Group>,
}

impl State {
    pub fn empty(cfg: &All) -> State {
        State {
            config: cfg.clone(),
            trust_db: TrustDB::default(),
            rules_db: RulesDB::default(),
            users: vec![],
            groups: vec![],
        }
    }

    pub fn load(cfg: &All) -> Result<State, Error> {
        let trust_db = load_trust_db(&cfg.system.trust_db_path)?;
        let rules_db = load_rules_db(&cfg.system.rules_file_path)?;
        Ok(State {
            config: cfg.clone(),
            trust_db,
            rules_db,
            users: load_users(),
            groups: load_groups(),
        })
    }

    pub fn load_checked(cfg: &All) -> Result<State, Error> {
        let state = State::load(cfg)?;
        let trust_db = check_trust_db(&state.trust_db)?;
        Ok(State { trust_db, ..state })
    }

    /// Apply a Changeset to this state, results in a new immutable state
    pub fn apply_trust_changes(&self, changes: Changeset) -> Self {
        println!("applying changeset to current state...");
        let modified = changes.apply(self.trust_db.clone());
        Self {
            config: self.config.clone(),
            trust_db: modified,
            rules_db: self.rules_db.clone(),
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
