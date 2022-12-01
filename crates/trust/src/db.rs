/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::collections::hash_map::Iter;
use std::collections::HashMap;

use crate::error::Error;
use crate::source::TrustSource;
use crate::source::TrustSource::{Ancillary, System};
use crate::stat::{check, Actual, Status};
use crate::Trust;

#[derive(Clone, Debug)]
pub enum Entry {
    Valid(Trust),
    WithWarning(Trust, String),
    Invalid { text: String, error: String },
    Comment(String),
}

/// Trust Database
/// A container for tracking trust entries and their metadata
/// Backed by a HashMap lookup table
#[derive(Clone, Debug)]
pub struct DB {
    pub(crate) lookup: HashMap<String, Rec>,
}

impl Default for DB {
    fn default() -> Self {
        DB::new()
    }
}

impl From<HashMap<String, Rec>> for DB {
    fn from(lookup: HashMap<String, Rec>) -> Self {
        Self { lookup }
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
    pub fn iter(&self) -> Iter<'_, String, Rec> {
        self.lookup.iter()
    }

    /// Get a Vec of record references
    pub fn values(&self) -> Vec<&Rec> {
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
    pub fn get(&self, k: &str) -> Option<&Rec> {
        self.lookup.get(k)
    }

    /// Put a record into the lookup table using the path of the trusted file
    /// This method takes only a record to ensure the key to value mapping is enforced.
    pub fn put(&mut self, v: Rec) -> Option<Rec> {
        self.lookup.insert(v.trusted.path.clone(), v)
    }

    /// Get a record from the lookup table using the path to the trusted file
    pub fn get_mut(&mut self, k: &str) -> Option<&mut Rec> {
        self.lookup.get_mut(k)
    }
}

/// Trust Record
/// Provides the trusted state and optionally the source of the trust and the actual state
#[derive(PartialEq, Eq, Clone, Debug)]
pub struct Rec {
    pub trusted: Trust,
    pub status: Option<Status>,
    actual: Option<Actual>,
    source: Option<TrustSource>,
    pub msg: Option<String>,
    pub origin: Option<String>,
}

impl Rec {
    /// Create an unsourced record
    pub fn new(t: Trust) -> Self {
        Rec {
            trusted: t,
            status: None,
            actual: None,
            source: None,
            msg: None,
            origin: None,
        }
    }

    pub fn new_from_system(t: Trust) -> Self {
        Self::new_from(t, System)
    }

    pub fn new_from_ancillary(t: Trust) -> Self {
        Self::new_from(t, Ancillary)
    }

    /// Create a sourced record
    pub(crate) fn new_from(t: Trust, source: TrustSource) -> Self {
        Rec {
            trusted: t,
            actual: None,
            status: None,
            source: Some(source),
            msg: None,
            origin: None,
        }
    }

    /// Is this record from system trust
    pub fn is_system(&self) -> bool {
        matches!(&self.source, Some(TrustSource::System))
    }

    /// Is this record from ancillary trust
    pub fn is_ancillary(&self) -> bool {
        !self.is_system()
    }

    /// Check a Rec into a Rec with updated status
    pub fn status_check(rec: Rec) -> Result<Rec, Error> {
        let status = check(&rec.trusted)?;
        Ok(Rec {
            status: Some(status),
            ..rec
        })
    }
}

#[cfg(test)]
mod tests {
    use std::iter::FromIterator;

    use crate::source::TrustSource::{Ancillary, System};

    use super::*;

    #[test]
    fn db_create() {
        assert!(DB::default().is_empty());
        assert!(DB::new().is_empty());
        assert!(DB::from(HashMap::new()).is_empty());

        let t1: Trust = Trust::new("/foo", 1, "0x00");
        let source = HashMap::from_iter(vec![(t1.path.clone(), Rec::new(t1.clone()))]);
        let db: DB = source.into();
        assert!(!db.is_empty());
        assert!(matches!(db.get(&t1.path), Some(n) if n.trusted == t1))
    }

    #[test]
    fn db_crud() {
        let mut db = DB::new();
        let t1: Trust = Trust::new("/foo", 1, "0x00");
        let t1b: Trust = Trust::new("/foo", 2, "0x01");
        let t2: Trust = Trust::new("/bar", 3, "0x02");

        assert_eq!(db.len(), 0);
        assert!(db.is_empty());

        // inserting trust uses its path
        assert!(db.put(Rec::new(t1.clone())).is_none());
        assert_eq!(*db.iter().next().unwrap().0, t1.path);
        assert_eq!(db.len(), 1);
        assert!(!db.is_empty());

        // trust entries are discrimiated by path
        assert!(db.put(Rec::new(t2.clone())).is_none());
        assert_eq!(db.get(&t2.path).unwrap().trusted.path, t2.path);
        assert_eq!(db.len(), 2);

        // overwriting trust with same path will return existing and replace it
        assert!(matches!(db.put(Rec::new(t1b.clone())), Some(n) if n.trusted == t1));
        assert_eq!(db.get(&t1b.path).unwrap().trusted.path, t1b.path);
        assert_eq!(db.len(), 2);
        assert!(!db.is_empty());
    }

    #[test]
    fn rec_create() {
        let t: Trust = Trust::new("/foo", 1, "0x00");

        let rec = Rec::new(t.clone());
        assert_eq!(rec.trusted, t);
        assert!(rec.actual.is_none());
        assert!(rec.source.is_none());

        let rec = Rec::new_from(t.clone(), System);
        assert_eq!(*rec.source.as_ref().unwrap(), System);
        assert!(rec.is_system());
        assert!(!rec.is_ancillary());

        let rec = Rec::new_from(t, TrustSource::Ancillary);
        assert_eq!(*rec.source.as_ref().unwrap(), TrustSource::Ancillary);
        assert!(!rec.is_system());
        assert!(rec.is_ancillary());
    }

    #[test]
    fn rec_source() {
        let t: Trust = Trust::new("/foo", 1, "0x00");

        assert!(!Rec::new(t.clone()).is_ancillary());
        assert!(!Rec::new(t.clone()).is_system());

        assert!(Rec::new_from(t.clone(), TrustSource::Ancillary).is_ancillary());
        assert!(Rec::new_from(t, System).is_system());
    }
}
