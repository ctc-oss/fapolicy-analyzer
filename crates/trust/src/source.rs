use std::fmt::{Display, Formatter};

use serde::Deserialize;
use serde::Serialize;

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
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
