use serde::Deserialize;
use serde::Serialize;

use crate::app;
use crate::sys;

pub const PROJECT_NAME: &str = "fapolicy-analyzer";

/// All configuration loaded from the user toml under XDG config dir
#[derive(Clone, Serialize, Deserialize, Default)]
pub struct All {
    pub system: sys::Config,
    pub application: app::Config,
}

impl All {
    pub fn data_dir(&self) -> &str {
        self.application.data_dir.as_str()
    }
}
