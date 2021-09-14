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
