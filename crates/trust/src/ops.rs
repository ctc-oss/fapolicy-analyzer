/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use fapolicy_util::sha::sha256_digest;
use std::collections::HashMap;
use std::fs::File;
use std::io::BufReader;

use crate::db::{Rec, DB};
use crate::error::Error;
use crate::ops::TrustOp::{Add, Del, Ins};
use crate::source::TrustSource;
use crate::Trust;

#[derive(Clone, Debug)]
pub enum TrustOp {
    Add(String),
    Del(String),
    Ins(String, u64, String),
}

impl TrustOp {
    fn run(&self, trust: &mut HashMap<String, Rec>) -> Result<(), Error> {
        match self {
            Add(path) => {
                let t = new_trust_record(path)?;
                let r = Rec::from_source(t, TrustSource::Ancillary);
                let r = Rec::status_check(r)?;
                trust.insert(r.trusted.path.clone(), r);
                Ok(())
            }
            Ins(path, size, hash) => {
                let t = Trust::new(path, *size, hash);
                let r = Rec::from_source(t, TrustSource::Ancillary);
                let r = Rec::status_check(r)?;
                trust.insert(r.trusted.path.clone(), r);
                Ok(())
            }
            Del(path) => {
                trust.remove(path);
                Ok(())
            }
        }
    }
}

fn to_pair(trust_op: &TrustOp) -> (String, String) {
    match trust_op {
        Add(path) => (path.to_string(), "Add".to_string()),
        Del(path) => (path.to_string(), "Del".to_string()),
        Ins(path, _size, _hash) => (path.to_string(), "Ins".to_string()),
    }
}

pub enum ChangesetErr {
    NotFound,
}

/// mutable append-only container for change operations
#[derive(Default, Clone, Debug)]
pub struct Changeset {
    changes: Vec<TrustOp>,
}

impl Changeset {
    pub fn new() -> Self {
        Changeset { changes: vec![] }
    }

    pub fn apply(&self, mut trust: DB) -> DB {
        for change in self.changes.iter() {
            change.run(&mut trust.lookup).unwrap()
        }
        trust
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

pub fn get_path_action_map(cs: &Changeset) -> HashMap<String, String> {
    cs.changes.iter().map(to_pair).collect()
}

fn new_trust_record(path: &str) -> Result<Trust, Error> {
    let f = File::open(path)?;
    let sha = sha256_digest(BufReader::new(&f))?;

    Ok(Trust {
        path: path.to_string(),
        size: f.metadata().unwrap().len(),
        hash: sha,
    })
}

pub trait InsChange {
    fn ins(&mut self, path: &str, size: u64, hash: &str);
}

impl InsChange for Changeset {
    fn ins(&mut self, path: &str, size: u64, hash: &str) {
        self.changes
            .push(Ins(path.to_string(), size, hash.to_string()))
    }
}

#[cfg(test)]
mod tests {
    use std::collections::HashMap;

    use super::*;

    fn make_trust(path: &str, size: u64, hash: &str) -> Trust {
        Trust {
            path: path.to_string(),
            size,
            hash: hash.to_string(),
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
        xs.ins(&expected.path, expected.size, &expected.hash);
        assert_eq!(xs.len(), 1);

        let store = xs.apply(DB::default());
        assert_eq!(store.len(), 1);

        let actual = store.get(&expected.path).unwrap();
        assert_eq!(actual.trusted, expected);
    }

    #[test]
    fn changeset_multiple_changes() {
        let mut xs = Changeset::new();
        xs.ins("/foo/bar", 1000, "12345");
        xs.ins("/foo/fad", 1000, "12345");
        assert_eq!(xs.len(), 2);

        let store = xs.apply(DB::default());
        assert_eq!(store.len(), 2);
    }

    #[test]
    fn changeset_del_existing() {
        let mut source = HashMap::new();
        source.insert(
            "/foo/bar".to_string(),
            Rec::without_source(make_default_trust_at("/foo/bar")),
        );

        let existing = DB::from(source);
        assert_eq!(existing.len(), 1);

        let mut xs = Changeset::new();
        xs.del("/foo/bar");
        assert_eq!(xs.len(), 1);

        let existing = xs.apply(existing);
        assert_eq!(existing.len(), 0);
    }

    #[test]
    fn changeset_add_then_del() {
        let mut xs = Changeset::new();
        xs.ins("/foo/bar", 1000, "12345");
        assert_eq!(xs.len(), 1);

        xs.del("/foo/bar");
        assert_eq!(xs.len(), 2);

        let store = xs.apply(DB::default());
        assert_eq!(store.len(), 0);
    }

    #[test]
    fn changeset_multiple_changes_same_file() {
        let expected = make_default_trust();

        let mut xs = Changeset::new();
        xs.ins(&expected.path, 1000, "12345");
        assert_eq!(xs.len(), 1);
        xs.ins(&expected.path, expected.size, &expected.hash);

        let store = xs.apply(DB::default());
        assert_eq!(store.len(), 1);

        let actual = store.get(&expected.path).unwrap();
        assert_eq!(actual.trusted, expected);
    }
}
