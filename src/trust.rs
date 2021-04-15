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
    Discrepancy(api::Trust, String),
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

/// load the fapolicyd backend lmdb database
/// parse the results into trust entries
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

/// load a fapolicyd ancillary file trust database
/// used to analyze the fapolicyd trust db for out of sync issues
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
    let mut v: Vec<&str> = s.rsplitn(3, ' ').collect();
    v.reverse();
    match v.as_slice() {
        [f, sz, sha] => Ok(api::Trust {
            path: f.to_string(),
            size: sz.parse().unwrap(),
            hash: sha.to_string(),
            source: t,
        }),
        _ => Err(format!("failed to read record; {}", s)),
    }
}

#[derive(Clone, Debug)]
enum TrustOp {
    Add(String),
    Del(String),
    Ins(String, u64, String),
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
            TrustOp::Ins(path, size, hash) => {
                trust.insert(
                    path.clone(),
                    Trust {
                        path: path.to_string(),
                        size: *size,
                        hash: hash.clone(),
                        source: TrustSource::Ancillary,
                    },
                );
                Ok(())
            }
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

/// mutable append-only container for change operations
#[derive(Clone, Debug)]
pub struct Changeset {
    changes: Vec<TrustOp>,
}

impl Changeset {
    pub fn new() -> Self {
        Changeset { changes: vec![] }
    }

    /// generate a modified trust map
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
        self.changes.is_empty()
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

trait InsChange {
    fn ins(&mut self, path: &str, size: u64, hash: &str);
}

impl InsChange for Changeset {
    fn ins(&mut self, path: &str, size: u64, hash: &str) {
        self.changes
            .push(TrustOp::Ins(path.to_string(), size, hash.to_string()))
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

    fn make_trust(path: &str, size: u64, hash: &str) -> Trust {
        Trust {
            path: path.to_string(),
            size,
            hash: hash.to_string(),
            source: TrustSource::Ancillary,
        }
    }

    fn make_default_trust_at(path: &str) -> Trust {
        Trust {
            path: path.to_string(),
            ..make_default_trust()
        }
    }

    fn make_default_trust() -> Trust {
        make_trust(
            "/home/user/my_ls",
            157984,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87",
        )
    }

    #[test]
    fn changeset_simple() {
        let expected = make_default_trust();

        let mut xs = Changeset::new();
        xs.ins(&*expected.path, expected.size, &*expected.hash);
        assert_eq!(xs.len(), 1);

        let store = xs.apply(HashMap::new());
        assert_eq!(store.len(), 1);

        let actual = store.get(&expected.path).unwrap();
        assert_eq!(*actual, expected);
    }

    #[test]
    fn changeset_multiple_changes() {
        let mut xs = Changeset::new();
        xs.ins("/foo/bar", 1000, "12345");
        xs.ins("/foo/fad", 1000, "12345");
        assert_eq!(xs.len(), 2);

        let store = xs.apply(HashMap::new());
        assert_eq!(store.len(), 2);
    }

    #[test]
    fn changeset_del_existing() {
        let mut existing = HashMap::new();
        existing.insert("/foo/bar".to_string(), make_default_trust_at("/foo/bar"));
        assert_eq!(existing.len(), 1);

        let mut xs = Changeset::new();
        xs.del("/foo/bar");
        assert_eq!(xs.len(), 1);

        let store = xs.apply(existing);
        assert_eq!(store.len(), 0);
    }

    #[test]
    fn changeset_add_then_del() {
        let mut xs = Changeset::new();
        xs.ins("/foo/bar", 1000, "12345");
        assert_eq!(xs.len(), 1);

        xs.del("/foo/bar");
        assert_eq!(xs.len(), 2);

        let store = xs.apply(HashMap::new());
        assert_eq!(store.len(), 0);
    }

    #[test]
    fn changeset_multiple_changes_same_file() {
        let expected = make_default_trust();

        let mut xs = Changeset::new();
        xs.ins(&*expected.path, 1000, "12345");
        assert_eq!(xs.len(), 1);
        xs.ins(&*expected.path, expected.size, &*expected.hash);

        let store = xs.apply(HashMap::new());
        assert_eq!(store.len(), 1);

        let actual = store.get(&expected.path).unwrap();
        assert_eq!(*actual, expected);
    }
}
