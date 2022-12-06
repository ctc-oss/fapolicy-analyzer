use crate::error::Error;
use crate::error::Error::{MalformattedTrustEntry, UnsupportedTrustType};
use crate::source::TrustSource;
use crate::source::TrustSource::{Ancillary, System};
use crate::Trust;

/// Parse a trust record from a string
/// Formatted as three space separated values
/// PATH SIZE HASH
pub fn trust_record(s: &str) -> Result<Trust, Error> {
    let mut v: Vec<&str> = s.rsplitn(3, ' ').collect();
    v.reverse();
    match v.as_slice() {
        [f, sz, sha] => Ok(Trust {
            path: f.trim().to_string(),
            size: sz.trim().parse()?,
            hash: sha.trim().to_string(),
        }),
        _ => Err(MalformattedTrustEntry(s.to_string())),
    }
}

pub(crate) fn strtyped_trust_record(s: &str, t: &str) -> Result<(Trust, TrustSource), Error> {
    match t {
        "1" => trust_record(s).map(|t| (t, System)),
        "2" => trust_record(s).map(|t| (t, Ancillary)),
        v => Err(UnsupportedTrustType(v.to_string())),
    }
}
