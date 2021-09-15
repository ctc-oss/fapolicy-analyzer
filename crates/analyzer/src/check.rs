use std::fs::File;
use std::io::{BufReader, ErrorKind};
use std::process::Command;
use std::time::UNIX_EPOCH;

use fapolicy_api::trust::Trust;
use fapolicy_trust::stat::{Actual, Status};
use fapolicy_util::sha::sha256_digest;

use crate::app::State;
use crate::error::Error;
use crate::error::Error::{FileIoError, GeneralError, MetaError};

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
        Ok(f) => match collect_actual(&f) {
            Ok(act) if act.hash == t.hash && act.size == t.size => {
                Ok(Status::Trusted(t.clone(), act))
            }
            Ok(act) => Ok(Status::Discrepancy(t.clone(), act)),
            Err(e) => Err(e),
        },
        Err(e) if e.kind() == ErrorKind::NotFound => Ok(Status::Missing(t.clone())),
        Err(e) => Err(FileIoError(e)),
    }
}

fn collect_actual(file: &File) -> Result<Actual, Error> {
    let meta = file.metadata()?;
    let sha = sha256_digest(BufReader::new(file))?;
    Ok(Actual {
        size: meta.len(),
        hash: sha,
        last_modified: meta
            .modified()
            .map_err(|e| MetaError(format!("{}", e)))?
            .duration_since(UNIX_EPOCH)
            .map_err(|_| MetaError("failed to convert to epoch seconds".into()))?
            .as_secs(),
    })
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
