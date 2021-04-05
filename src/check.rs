use crate::api::Trust;
use crate::app::State;
use crate::sha::sha256_digest;
use crate::trust::Status;
use std::fs::File;
use std::io::BufReader;

/// check for sync between fapolicyd and rpmdb
/// can return false on the first mismatch
pub fn rpm_sync(_app: &State) -> bool {
    true
}

/// check for sync between fapolicyd and file trust
/// can return false on the first mismatch
pub fn file_sync(_app: &State) -> bool {
    true
}

/// check status of trust against the filesystem
pub fn trust_status(t: &Trust) -> Result<Status, String> {
    match File::open(&t.path) {
        Ok(f) => match sha256_digest(BufReader::new(f)) {
            Ok(sha) if sha == t.hash => Ok(Status::Trusted(t.clone())),
            Ok(sha) => Ok(Status::Untrusted(t.clone(), sha)),
            Err(e) => Err(format!("sha256 op failed, {}", e)),
        },
        _ => Err(format!("WARN: {} not found", t.path)),
    }
}
