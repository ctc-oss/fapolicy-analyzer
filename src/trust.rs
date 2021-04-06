use std::collections::HashMap;
use std::fs::File;
use std::io::prelude::*;
use std::io::BufReader;
use std::path::Path;

use lmdb::{Cursor, Environment, Transaction};

use crate::api;
use crate::api::{Trust, TrustSource};
use crate::sha::sha256_digest;
use crate::trust::TrustOp::{Add, Del};

/// Trust status tag
/// T / U / unk
#[derive(Clone)]
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

// todo;; https://github.com/rust-lang/rust/issues/74773
fn str_split_once(s: &str) -> (&str, String) {
    let mut splits = s.split(' ');
    let head = splits.next().unwrap();
    let tail = splits.collect::<Vec<&str>>().join(" ");
    (head, tail)
}

impl From<TrustPair> for api::Trust {
    fn from(kv: TrustPair) -> Self {
        // todo;; let v = kv.v.split_once(' ').unwrap().1;
        let (t, v) = str_split_once(&kv.v);
        parse_strtyped_trust_record(format!("{} {}", kv.k, v).as_str(), t).unwrap()
    }
}

pub fn load_trust_db(path: &str) -> Vec<api::Trust> {
    let env = Environment::new().set_max_dbs(1).open(Path::new(path));
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
                    .map(TrustPair::new)
                    .map(|kv| kv.into())
                    .collect()
            })
        })
        .unwrap()
        .unwrap()
}

pub fn load_ancillary_trust(path: &str) -> Vec<api::Trust> {
    let f = File::open(path);
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

fn parse_strtyped_trust_record(s: &str, t: &str) -> Result<api::Trust, String> {
    match t {
        "1" => parse_typed_trust_record(s, TrustSource::System),
        "2" => parse_typed_trust_record(s, TrustSource::Ancillary),
        _ => Err("unknown trust type".to_string()),
    }
}

fn parse_trust_record(s: &str) -> Result<api::Trust, String> {
    parse_typed_trust_record(s, TrustSource::Ancillary)
}

fn parse_typed_trust_record(s: &str, t: api::TrustSource) -> Result<api::Trust, String> {
    let v: Vec<&str> = s.split(' ').collect();
    match v.as_slice() {
        [f, sz, sha] => Ok(api::Trust {
            path: f.to_string(),
            size: sz.parse().unwrap(),
            hash: sha.to_string(),
            source: t,
        }),
        _ => Err(String::from("failed to read record")),
    }
}

#[derive(Clone, Debug)]
enum TrustOp {
    Add(String),
    Del(String),
}

impl TrustOp {
    fn run(&self, trust: &mut HashMap<String, Trust>) -> Result<(), String> {
        match self {
            TrustOp::Add(path) => match new_trust_record(&path) {
                Ok(t) => {
                    trust.insert(path.to_string(), t);
                    Ok(())
                }
                Err(_) => Err("failed to add trust".to_string()),
            },
            TrustOp::Del(path) => {
                trust.remove(path);
                Ok(())
            }
        }
    }
}

pub enum ChangesetErr {
    NotFound,
}

#[derive(Clone, Debug)]
pub struct Changeset {
    changes: Vec<TrustOp>,
}

impl Changeset {
    pub fn new() -> Self {
        Changeset { changes: vec![] }
    }

    pub fn apply(&self, trust: HashMap<String, Trust>) -> HashMap<String, Trust> {
        let mut modified = trust;
        for change in self.changes.iter() {
            change.run(&mut modified).unwrap()
        }
        modified
    }

    pub fn add(&mut self, path: &str) {
        self.changes.push(Add(path.to_string()))
    }

    pub fn del(&mut self, path: &str) {
        self.changes.push(Del(path.to_string()))
    }

    pub fn len(&self) -> usize {
        self.changes.len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

impl ::std::default::Default for Changeset {
    fn default() -> Self {
        Self { changes: vec![] }
    }
}

fn new_trust_record(path: &str) -> Result<Trust, String> {
    let f = File::open(path).map_err(|_| "failed to open file".to_string())?;
    let sha = sha256_digest(BufReader::new(&f)).map_err(|_| "failed to hash file".to_string())?;

    Ok(Trust {
        path: path.to_string(),
        size: f.metadata().unwrap().len(),
        hash: sha,
        source: TrustSource::Ancillary,
    })
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
        assert_eq!(
            e.hash,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
        );
    }
}
