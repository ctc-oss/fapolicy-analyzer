/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::collections::hash_map::Iter;
use std::collections::HashMap;

use crate::Rule;

/// Rules Database
/// A container for rules and their metadata
#[derive(Clone, Debug)]
pub struct DB {
    lookup: HashMap<usize, Rule>,
}

impl Default for DB {
    fn default() -> Self {
        DB::new()
    }
}

impl From<Vec<Rule>> for DB {
    fn from(src: Vec<Rule>) -> Self {
        let lookup: HashMap<usize, Rule> = src
            .iter()
            .enumerate()
            // fapolicyd rules are 1-based index
            .map(|(k, v)| (k + 1, v.clone()))
            .collect();
        DB { lookup }
    }
}

impl DB {
    /// Create a new empty database
    pub fn new() -> Self {
        DB {
            lookup: HashMap::default(),
        }
    }

    /// Get a record iterator to the underlying lookup table
    pub fn iter(&self) -> Iter<'_, usize, Rule> {
        self.lookup.iter()
    }

    /// Get a Vec of record references
    pub fn values(&self) -> Vec<&Rule> {
        self.lookup.values().collect()
    }

    /// Get the number of records in the lookup table
    pub fn len(&self) -> usize {
        self.lookup.len()
    }

    /// Test if the lookup table is empty
    pub fn is_empty(&self) -> bool {
        self.lookup.is_empty()
    }

    /// Get a record from the lookup table using the path to the trusted file
    pub fn get(&self, id: usize) -> Option<&Rule> {
        self.lookup.get(&id)
    }
}

#[cfg(test)]
mod tests {
    use crate::{Decision, Object, Permission, Subject};

    use super::*;

    #[test]
    fn db_create() {
        assert!(DB::default().is_empty());
        assert!(DB::new().is_empty());

        let r1: Rule = Rule::new(
            Subject::all(),
            Permission::Any,
            Object::all(),
            Decision::Allow,
        );
        let db: DB = vec![r1].into();
        assert!(!db.is_empty());
        assert!(db.get(1).is_some());
    }

    #[test]
    fn maintain_order() {
        assert!(DB::default().is_empty());
        assert!(DB::new().is_empty());

        let subjs = vec!["fee", "fi", "fo", "fum", "this", "is", "such", "fun"];
        let rules: Vec<Rule> = subjs
            .iter()
            .map(|s| {
                Rule::new(
                    Subject::from_exe(s),
                    Permission::Any,
                    Object::all(),
                    Decision::Allow,
                )
            })
            .collect();

        let db: DB = rules.into();
        assert!(!db.is_empty());
        assert_eq!(db.len(), 8);

        for s in subjs.iter().enumerate() {
            assert_eq!(db.get(s.0 + 1).unwrap().subj.exe().unwrap(), *s.1);
        }
    }
}
