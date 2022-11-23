use crate::db::{Rec, DB};
use crate::error::Error;
use crate::error::Error::{
    LmdbNotFound, LmdbPermissionDenied, LmdbReadFail, MalformattedTrustEntry, UnsupportedTrustType,
};
use crate::read::parse_trust_record;
use crate::source::TrustSource;
use crate::source::TrustSource::{Ancillary, System};
use crate::Trust;
use lmdb::{Cursor, Environment, Transaction};
use std::collections::HashMap;
use std::path::Path;

// 1. checking disk for actual status

// 2. checking lmdb for sync status
fn parse_strtyped_trust_record(s: &str, t: &str) -> Result<(Trust, TrustSource), Error> {
    match t {
        "1" => parse_trust_record(s).map(|t| (t, System)),
        "2" => parse_trust_record(s).map(|t| (t, Ancillary)),
        v => Err(UnsupportedTrustType(v.to_string())),
    }
}

pub(crate) struct TrustPair {
    pub k: String,
    pub v: String,
}

impl TrustPair {
    fn new(b: (&[u8], &[u8])) -> TrustPair {
        TrustPair {
            k: String::from_utf8(Vec::from(b.0)).unwrap(),
            v: String::from_utf8(Vec::from(b.1)).unwrap(),
        }
    }
}

impl From<TrustPair> for (String, Rec) {
    fn from(kv: TrustPair) -> Self {
        let (tt, v) = kv.v.split_once(' ').unwrap();
        let (t, s) = parse_strtyped_trust_record(format!("{} {}", kv.k, v).as_str(), tt)
            .expect("failed to parse_strtyped_trust_record");
        (t.path.clone(), Rec::new_from(t, s))
    }
}

/// load the fapolicyd backend lmdb database
/// parse the results into trust entries
pub fn db_sync(db: &mut DB, lmdb_path: &str) -> Result<DB, Error> {
    let env = Environment::new().set_max_dbs(1).open(Path::new(lmdb_path));
    let env = match env {
        Ok(e) => e,
        Err(lmdb::Error::Other(2)) => return Err(LmdbNotFound(lmdb_path.to_string())),
        Err(lmdb::Error::Other(13)) => return Err(LmdbPermissionDenied(lmdb_path.to_string())),
        Err(e) => return Err(LmdbReadFail(e)),
    };

    let lmdb = env.open_db(Some("trust.db")).map_err(LmdbReadFail)?;
    let c = env.begin_ro_txn()?.open_ro_cursor(lmdb)?;
    for i in c.iter() {}
    let lookup: HashMap<String, Rec> = env
        .begin_ro_txn()
        .map(|t| {
            t.open_ro_cursor(lmdb).map(|mut c| {
                c.iter()
                    .map(|c| c.unwrap())
                    .map(|kv| TrustPair::new(kv).into())
                    .collect()
            })
        })
        .unwrap()
        .map_err(LmdbReadFail)
        .unwrap();

    Ok(DB::from(lookup))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    // todo;; additional coverage for type 2 and invalid type
    fn parse_trust_pair() {
        let tp = TrustPair::new((
            "/home/user/my-ls".as_bytes(),
            "1 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87".as_bytes(),
        ));
        let (_, r) = tp.into();

        assert_eq!(r.trusted.path, "/home/user/my-ls");
        assert_eq!(r.trusted.size, 157984);
        assert_eq!(
            r.trusted.hash,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
        );
    }
}
