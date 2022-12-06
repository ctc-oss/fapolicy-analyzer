use crate::db::{Rec, DB};
use crate::error::Error;
use crate::read;
use std::collections::HashMap;
use std::path::Path;

use lmdb::{Cursor, Environment, Transaction};

use crate::check::TrustPair;
use crate::error::Error::{LmdbFailure, LmdbNotFound, LmdbPermissionDenied};

/// Load a Trust DB
/// System entries are sourced from lmdb
/// File entries are sourced from trust.d and fapolicyd.trust
pub fn trust_db(lmdb: &Path, trust_d: &Path, trust_file: Option<&Path>) -> Result<DB, Error> {
    let mut db = system_from_lmdb(lmdb)?;
    for (s, t) in read::file_trust(trust_d, trust_file)? {
        db.put(Rec::new_from_source(t, s));
    }
    Ok(db)
}

pub(crate) fn system_from_lmdb(lmdb: &Path) -> Result<DB, Error> {
    let mut db = from_lmdb(lmdb)?;
    db.filter(|e| e.is_system());
    Ok(db)
}

/// load the fapolicyd backend lmdb database
/// parse the results into trust entries
pub fn from_lmdb(lmdb: &Path) -> Result<DB, Error> {
    let env = Environment::new().set_max_dbs(1).open(lmdb);
    let env = match env {
        Ok(e) => e,
        Err(lmdb::Error::Other(2)) => return Err(LmdbNotFound(lmdb.display().to_string())),
        Err(lmdb::Error::Other(13)) => {
            return Err(LmdbPermissionDenied(lmdb.display().to_string()))
        }
        Err(e) => return Err(LmdbFailure(e)),
    };

    let lmdb = env.open_db(Some("trust.db"))?;
    let tx = env.begin_ro_txn()?;
    let mut c = tx.open_ro_cursor(lmdb)?;
    let lookup: HashMap<String, Rec> = c
        .iter()
        .map(|i| i.map(|kv| TrustPair::new(kv).into()).unwrap())
        .collect();

    Ok(DB::from(lookup))
}

const USR_SHARE_ALLOWED_EXTS: [&str; 15] = [
    "pyc", "pyo", "py", "rb", "pl", "stp", "js", "jar", "m4", "php", "el", "pm", "lua", "class",
    "elc",
];

/// filtering logic as implemented by fapolicyd rpm backend
pub fn keep_entry(p: &str) -> bool {
    match p {
        s if s.starts_with("/usr/share") => {
            USR_SHARE_ALLOWED_EXTS.iter().any(|ext| s.ends_with(*ext)) || s.contains("/libexec/")
        }
        s if s.starts_with("/usr/src") => s.contains("/scripts/") || s.contains("/tools/objtool/"),
        s if s.starts_with("/usr/include") => false,
        _ => true,
    }
}
