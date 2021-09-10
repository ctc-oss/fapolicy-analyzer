use std::fs::File;
use std::io::prelude::*;
use std::io::BufReader;
use std::path::Path;

use lmdb::{Cursor, Environment, Transaction};

use crate::error::Error;
use crate::error::Error::{
    LmdbNotFound, LmdbPermissionDenied, LmdbReadFail, MalformattedTrustEntry, TrustSourceNotFound,
    UnsupportedTrustType,
};
use crate::trust::TrustSource::{Ancillary, System};
use crate::trust::{Trust, TrustSource};

struct TrustPair {
    k: String,
    v: String,
}

impl TrustPair {
    fn new(b: (&[u8], &[u8])) -> TrustPair {
        TrustPair {
            k: String::from_utf8(Vec::from(b.0)).unwrap(),
            v: String::from_utf8(Vec::from(b.1)).unwrap(),
        }
    }
}

impl From<TrustPair> for Trust {
    fn from(kv: TrustPair) -> Self {
        let (t, v) = kv.v.split_once(' ').unwrap();
        parse_strtyped_trust_record(format!("{} {}", kv.k, v).as_str(), t).unwrap()
    }
}

/// load the fapolicyd backend lmdb database
/// parse the results into trust entries
pub fn load_trust_db(path: &str) -> Result<Vec<Trust>, Error> {
    let env = Environment::new().set_max_dbs(1).open(Path::new(path));
    let env = match env {
        Ok(e) => e,
        Err(lmdb::Error::Other(2)) => return Err(LmdbNotFound(path.to_string())),
        Err(lmdb::Error::Other(13)) => return Err(LmdbPermissionDenied(path.to_string())),
        Err(e) => return Err(LmdbReadFail(e)),
    };

    let db = env.open_db(Some("trust.db")).map_err(LmdbReadFail)?;
    env.begin_ro_txn()
        .map(|t| {
            t.open_ro_cursor(db).map(|mut c| {
                c.iter()
                    .map(|c| c.unwrap())
                    .map(TrustPair::new)
                    .map(|kv| kv.into())
                    .collect()
            })
        })
        .unwrap()
        .map_err(LmdbReadFail)
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

fn parse_strtyped_trust_record(s: &str, t: &str) -> Result<Trust, Error> {
    match t {
        "1" => parse_typed_trust_record(s, System),
        "2" => parse_typed_trust_record(s, Ancillary),
        v => Err(UnsupportedTrustType(v.to_string())),
    }
}

fn parse_trust_record(s: &str) -> Result<Trust, Error> {
    parse_typed_trust_record(s, Ancillary)
}

fn parse_typed_trust_record(s: &str, t: TrustSource) -> Result<Trust, Error> {
    let mut v: Vec<&str> = s.rsplitn(3, ' ').collect();
    v.reverse();
    match v.as_slice() {
        [f, sz, sha] => Ok(Trust {
            path: f.to_string(),
            size: sz.parse().unwrap(),
            hash: sha.to_string(),
            source: t,
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
        let t: Trust = tp.into();

        assert_eq!(t.path, "/home/user/my-ls");
        assert_eq!(t.size, 157984);
        assert_eq!(
            t.hash,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
        );
    }
}
