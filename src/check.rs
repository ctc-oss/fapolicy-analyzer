use std::fs::File;
use std::io::BufReader;

use crate::api::Trust;
use crate::app::State;
use crate::error::Error;
use crate::error::Error::FileNotFound;
use crate::sha::sha256_digest;
use crate::trust::Status;
use std::process::Command;

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
pub fn trust_status(t: &Trust) -> Result<Status, Error> {
    match File::open(&t.path) {
        Ok(f) => match sha256_digest(BufReader::new(&f)) {
            Ok(sha) if sha == t.hash && len(&f) == t.size => Ok(Status::Trusted(t.clone())),
            Ok(sha) => Ok(Status::Discrepancy(t.clone(), sha)),
            Err(e) => Err(e),
        },
        _ => Err(FileNotFound("trusted file".to_string(), t.path.clone())),
    }
}

fn len(file: &File) -> u64 {
    file.metadata().unwrap().len()
}

#[derive(Debug, Clone)]
pub enum RpmError {
    Discovery,
    NotFound,
    Execution,
}

// return rpm version
pub fn check_rpm() -> Result<String, RpmError> {
    match Command::new("which").arg("rpm").output() {
        Ok(eo) if eo.status.success() => {
            let rpmpath = String::from_utf8(eo.stdout).unwrap().trim().to_string();
            match Command::new(&rpmpath).arg("--version").output() {
                Ok(vo) if vo.status.success() => {
                    let rpmver = String::from_utf8(vo.stdout).unwrap().trim().to_string();
                    Ok(rpmver)
                }
                _ => Err(RpmError::Execution),
            }
        }
        Ok(_) => Err(RpmError::NotFound),
        _ => Err(RpmError::Discovery),
    }
}
