use serde::Deserialize;
use serde::Serialize;
use std::fmt::{Display, Formatter};

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub enum TrustSource {
    Ancillary,
    System,
}

impl Display for TrustSource {
    fn fmt(&self, f: &mut Formatter) -> std::fmt::Result {
        match *self {
            TrustSource::Ancillary => write!(f, "Ancillary"),
            TrustSource::System => write!(f, "System"),
        }
    }
}

// todo;; from 0,1,2 for TrustSource

// intent to match up with the fapolicyd trust db
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Trust {
    pub path: String,
    pub size: u64,
    pub hash: String,
    pub source: TrustSource,
}

impl Trust {
    pub fn new(path: &str, size: u64, hash: &str, source: TrustSource) -> Trust {
        Trust {
            path: path.to_string(),
            size,
            hash: hash.to_string(),
            source,
        }
    }
}
