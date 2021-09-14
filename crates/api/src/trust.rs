use serde::Deserialize;
use serde::Serialize;
use std::fmt::{Display, Formatter};

/// The properties that impact Trust reasoning
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Trust {
    pub path: String,
    pub size: u64,
    pub hash: String,
}

impl Trust {
    pub fn new(path: &str, size: u64, hash: &str) -> Trust {
        Trust {
            path: path.to_string(),
            size,
            hash: hash.to_string(),
        }
    }
}
