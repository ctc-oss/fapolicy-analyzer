use serde::Deserialize;
use serde::Serialize;

use crate::sys;

#[derive(Clone, Serialize, Deserialize, Default)]
pub struct All {
    pub system: sys::Config,
}

pub fn load() -> All {
    confy::load("fapolicy-analyzer").expect("unable to load user configuration")
}
