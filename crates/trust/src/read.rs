use std::collections::HashMap;
use std::fs::File;
use std::io::prelude::*;
use std::io::BufReader;
use std::path::Path;

use lmdb::{Cursor, Environment, Transaction};

use fapolicy_api::trust::Trust;

use crate::db::{Rec, DB};
use crate::error::Error;
use crate::error::Error::{
    LmdbNotFound, LmdbPermissionDenied, LmdbReadFail, MalformattedTrustEntry, TrustSourceNotFound,
    UnsupportedTrustType,
};
use crate::source::TrustSource;
use crate::source::TrustSource::{Ancillary, System};

// todo;; why do we need this? why not go straight to Meta
pub(crate) struct TrustEntry {
    pub path: String,
    pub trust: Trust,
    source: TrustSource,
}

impl From<TrustPair> for TrustEntry {
    fn from(kv: TrustPair) -> Self {
        let (tt, v) = kv.v.split_once(' ').unwrap();
        let (t, s) = parse_strtyped_trust_record(format!("{} {}", kv.k, v).as_str(), tt)
            .expect("failed to parse_strtyped_trust_record");

        TrustEntry {
            path: t.path.clone(),
            trust: t,
            source: s,
        }
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
    let lookup: HashMap<String, Rec> = env
        .begin_ro_txn()
        .map(|t| {
            t.open_ro_cursor(db).map(|mut c| {
                c.iter()
                    .map(|c| c.unwrap())
                    .map(|kv| TrustPair::new(kv).into())
                    .map(|e: TrustEntry| (e.path, Rec::with(e.trust)))
                    .collect()
            })
        })
        .unwrap()
        .map_err(LmdbReadFail)
        .unwrap();

    Ok(DB::new(lookup))
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

        assert_eq!(te.path, "/home/user/my-ls");
        assert_eq!(te.trust.size, 157984);
        assert_eq!(
            te.trust.hash,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
        );
    }
}
