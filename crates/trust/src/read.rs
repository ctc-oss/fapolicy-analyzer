use std::fs::File;
use std::io::prelude::*;
use std::io::BufReader;
use std::path::Path;

use lmdb::{Cursor, Environment, Transaction};

use crate::source::TrustSource;
use crate::source::TrustSource::{Ancillary, System};
use fapolicy_api::trust::Trust;

use crate::db::{TrustEntry, TrustRec, DB};
use crate::error::Error;
use crate::error::Error::{
    LmdbNotFound, LmdbPermissionDenied, LmdbReadFail, MalformattedTrustEntry, TrustSourceNotFound,
    UnsupportedTrustType,
};
use std::collections::HashMap;

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

/// load the fapolicyd backend lmdb database
/// parse the results into trust entries
pub fn load_trust_db(path: &str) -> Result<DB, Error> {
    let env = Environment::new().set_max_dbs(1).open(Path::new(path));
    let env = match env {
        Ok(e) => e,
        Err(lmdb::Error::Other(2)) => return Err(LmdbNotFound(path.to_string())),
        Err(lmdb::Error::Other(13)) => return Err(LmdbPermissionDenied(path.to_string())),
        Err(e) => return Err(LmdbReadFail(e)),
    };

    let db = env.open_db(Some("trust.db")).map_err(LmdbReadFail)?;
    let lookup: HashMap<TrustRec, Trust> = env
        .begin_ro_txn()
        .map(|t| {
            t.open_ro_cursor(db).map(|mut c| {
                c.iter()
                    .map(|c| c.unwrap())
                    .map(TrustPair::new)
                    .map(|kv| {
                        let te: TrustEntry = kv.into();
                        te
                    })
                    .map(|e| (e.k, e.v))
                    .collect()
            })
        })
        .unwrap()
        .map_err(LmdbReadFail)
        .unwrap();

    Ok(DB::default())
}

/// load a fapolicyd ancillary file trust database
/// used to analyze the fapolicyd trust db for out of sync issues
pub fn load_ancillary_trust(path: &str) -> Result<Vec<Trust>, Error> {
    match File::open(path) {
        Ok(e) => Ok(read_ancillary_trust(e)),
        _ => Err(TrustSourceNotFound(Ancillary, path.to_string())),
    }
}

fn read_ancillary_trust(f: File) -> Vec<Trust> {
    let r = BufReader::new(f);
    r.lines()
        .map(|r| r.unwrap())
        .filter(|s| !s.is_empty() && !s.starts_with('#'))
        .map(|l| parse_trust_record(&l).unwrap())
        .collect()
}

pub(crate) fn parse_strtyped_trust_record(s: &str, t: &str) -> Result<(Trust, TrustSource), Error> {
    match t {
        "1" => parse_typed_trust_record(s).map(|t| (t, System)),
        "2" => parse_typed_trust_record(s).map(|t| (t, Ancillary)),
        v => Err(UnsupportedTrustType(v.to_string())),
    }
}

fn parse_trust_record(s: &str) -> Result<Trust, Error> {
    parse_typed_trust_record(s)
}

fn parse_typed_trust_record(s: &str) -> Result<Trust, Error> {
    let mut v: Vec<&str> = s.rsplitn(3, ' ').collect();
    v.reverse();
    match v.as_slice() {
        [f, sz, sha] => Ok(Trust {
            path: f.to_string(),
            size: sz.parse().unwrap(),
            hash: sha.to_string(),
        }),
        _ => Err(MalformattedTrustEntry(s.to_string())),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_record() {
        let s =
            "/home/user/my-ls 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87";
        let e = parse_trust_record(s).unwrap();
        assert_eq!(e.path, "/home/user/my-ls");
        assert_eq!(e.size, 157984);
        assert_eq!(
            e.hash,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
        );
    }

    #[test]
    fn parse_record_with_space() {
        let s =
            "/home/user/my ls 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87";
        let e = parse_trust_record(s).unwrap();
        assert_eq!(e.path, "/home/user/my ls");
        assert_eq!(e.size, 157984);
        assert_eq!(
            e.hash,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
        );
    }

    #[test]
    // todo;; additional coverage for type 2 and invalid type
    fn parse_trust_pair() {
        let tp = TrustPair::new((
            "/home/user/my-ls".as_bytes(),
            "1 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87".as_bytes(),
        ));
        let te: TrustEntry = tp.into();

        assert_eq!(te.k.path, "/home/user/my-ls");
        assert_eq!(te.v.size, 157984);
        assert_eq!(
            te.v.hash,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
        );
    }
}
