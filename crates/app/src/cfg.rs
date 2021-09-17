use crate::{app, sys};
use serde::Deserialize;
use serde::Serialize;

pub const PROJECT_NAME: &str = "fapolicy-analyzer";

/// All configuration loaded from the user toml under XDG config dir
#[derive(Clone, Serialize, Deserialize, Default)]
pub struct All {
    pub system: sys::Config,
    pub application: app::Config,
}

impl All {
    pub fn load() -> All {
        confy::load(PROJECT_NAME).expect("unable to load xdg configuration")
    }

    pub fn data_dir(&self) -> &str {
        self.application.data_dir.as_str()
    }
}
