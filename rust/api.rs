use serde::Deserialize;
use serde::Serialize;

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub enum TrustSource {
    System,
    Ancillary,
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
