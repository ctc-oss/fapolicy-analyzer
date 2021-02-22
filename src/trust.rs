use std::fs::File;
use std::io::prelude::*;
use std::io::BufReader;
use std::path::Path;

use lmdb::{Cursor, Environment, Transaction};

use sha::sha256_digest;

use crate::api;
use crate::fapolicyd;
use crate::sha;

/// Trust status tag
/// T / U / unk
pub enum Status {
    /// No entry in database
    Unknown(api::Trust),
    /// filesystem matches database
    Trusted(api::Trust),
    /// filesystem does not match database
    /// lhs expected, rhs actual
    Untrusted(api::Trust, String),
    // todo;; what about file does not exist?
}

pub fn check(t: api::Trust) -> Result<Status, String> {
    match File::open(&t.path) {
        Ok(f) => match sha256_digest(BufReader::new(f)) {
            Ok(sha) if sha == t.hash => Ok(Status::Trusted(t)),
            Ok(sha) => Ok(Status::Untrusted(t, sha)),
            Err(e) => Err(format!("sha256 op failed, {}", e)),
        },
        _ => Err(format!("WARN: {} not found", t.path)),
    }
}

struct TrustKV {
    k: String,
    v: String,
}

impl TrustKV {
    fn new(b: (&[u8], &[u8])) -> TrustKV {
        TrustKV {
            k: String::from_utf8(Vec::from(b.0)).unwrap(),
            v: String::from_utf8(Vec::from(b.1)).unwrap(),
        }
    }
}

// todo;; https://github.com/rust-lang/rust/issues/74773
fn str_split_once(s: &str) -> (&str, String) {
    let mut splits = s.split(' ');
    let head = splits.next().unwrap();
    let tail = splits.collect::<Vec<&str>>().join(" ");
    (head, tail)
}

impl From<TrustKV> for api::Trust {
    fn from(kv: TrustKV) -> Self {
        // todo;; let v = kv.v.split_once(' ').unwrap().1;
        let v = str_split_once(&kv.v).1;
        parse_trust_record(format!("{} {}", kv.k, v).as_str()).unwrap()
    }
}

pub fn load_trust_db(path: &Option<String>) -> Vec<api::Trust> {
    let dbdir = match path {
        Some(ref p) => Path::new(p),
        None => Path::new(fapolicyd::TRUST_DB_PATH),
    };

    let env = Environment::new().set_max_dbs(1).open(dbdir);
    let env = match env {
        Ok(e) => e,
        _ => {
            println!("WARN: fapolicyd trust db was not found");
            return vec![];
        }
    };

    let db = env.open_db(Some("trust.db")).expect("load trust.db");

    env.begin_ro_txn()
        .map(|t| {
            t.open_ro_cursor(db).map(|mut c| {
                c.iter()
                    .map(|c| c.unwrap())
                    .map(TrustKV::new)
                    .map(|kv| kv.into())
                    .collect()
            })
        })
        .unwrap()
        .unwrap()
}

pub fn load_ancillary_trust(path: &Option<String>) -> Vec<api::Trust> {
    let f = File::open(
        path.as_ref()
            .unwrap_or(&fapolicyd::TRUST_FILE_PATH.to_string()),
    );
    let f = match f {
        Ok(e) => e,
        _ => {
            println!("WARN: fapolicyd trust file was not found");
            return vec![];
        }
    };

    let r = BufReader::new(f);

    r.lines()
        .map(|r| r.unwrap())
        .filter(|s| !s.is_empty() && !s.starts_with('#'))
        .map(|l| parse_trust_record(&l).unwrap())
        .collect()
}

fn parse_trust_record(s: &str) -> Result<api::Trust, String> {
    println!("parsing trust record {}", s);
    let v: Vec<&str> = s.split(' ').collect();
    match v.as_slice() {
        [f, sz, sha] => Ok(api::Trust {
            path: f.to_string(),
            size: sz.parse().unwrap(),
            hash: sha.to_string(),
            source: api::TrustSource::Ancillary,
        }),
        _ => Err(String::from("failed to read record")),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn deserialize_entry() {
        let s =
            "/home/user/my-ls 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87";
        let e = parse_trust_record(s).unwrap();
        assert_eq!(e.path, "/home/user/my-ls");
        assert_eq!(e.size, 157984);
        assert_eq!(e.hash, s.to_string());
    }
}
