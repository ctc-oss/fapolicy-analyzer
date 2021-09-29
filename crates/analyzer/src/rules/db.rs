use std::collections::hash_map::Iter;
use std::collections::HashMap;

use crate::rules::Rule;

/// Rules Database
/// A container for rules and their metadata
/// Backed by a HashMap lookup table
#[derive(Clone, Debug)]
pub struct DB {
    pub(crate) lookup: HashMap<usize, Rule>,
}

impl Default for DB {
    fn default() -> Self {
        DB::new()
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
        // fapolicyd rules are indexed from 1
        self.lookup.get(&(id - 1))
    }
}

#[cfg(test)]
mod tests {
    use std::iter::FromIterator;

    use super::*;
    use crate::rules::{Decision, Object, Permission, Subject};

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
        let lookup = HashMap::from_iter(vec![(0, r1)]);
        let db: DB = DB { lookup };
        assert!(!db.is_empty());
        assert!(db.get(1).is_some());
    }
}
