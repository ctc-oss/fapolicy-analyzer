use std::collections::hash_map::Iter;
use std::collections::HashMap;

use fapolicy_api::trust::Trust;

use crate::source::TrustSource;
use crate::stat::Actual;

#[derive(Clone, Debug)]
pub struct DB {
    pub(crate) lookup: HashMap<String, Rec>,
}

impl Default for DB {
    fn default() -> Self {
        DB {
            lookup: HashMap::default(),
        }
    }
}

impl From<HashMap<String, Rec>> for DB {
    fn from(lookup: HashMap<String, Rec>) -> Self {
        Self { lookup }
    }
}

impl DB {
    pub fn new() -> Self {
        DB::default()
    }

    pub fn iter(&self) -> Iter<'_, String, Rec> {
        self.lookup.iter()
    }

    pub fn len(&self) -> usize {
        self.lookup.len()
    }

    pub fn is_empty(&self) -> bool {
        self.lookup.is_empty()
    }

    pub fn get(&self, k: &str) -> Option<&Rec> {
        self.lookup.get(k)
    }

    pub fn put(&mut self, v: Rec) -> Option<Rec> {
        self.lookup.insert(v.trusted.path.clone(), v)
    }
}

#[derive(PartialEq, Eq, Clone, Debug)]
pub struct Rec {
    pub trusted: Trust,
    actual: Option<Actual>,
    source: Option<TrustSource>,
}

impl Rec {
    pub fn new(t: Trust) -> Self {
        Rec {
            trusted: t,
            actual: None,
            source: None,
        }
    }

    pub(crate) fn new_from(t: Trust, source: TrustSource) -> Self {
        Rec {
            trusted: t,
            actual: None,
            source: Some(source),
        }
    }

    pub fn is_sys(&self) -> bool {
        matches!(&self.source, Some(TrustSource::System))
    }

    pub fn is_ancillary(&self) -> bool {
        matches!(&self.source, Some(TrustSource::Ancillary))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::source::TrustSource::{Ancillary, System};
    use std::iter::FromIterator;

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
    fn rec_new() {
        let t: Trust = Trust::new("/foo", 1, "0x00");

        let rec = Rec::new(t.clone());
        assert_eq!(rec.trusted, t);
        assert!(rec.actual.is_none());
        assert!(rec.source.is_none());

        let rec = Rec::new_from(t.clone(), System);
        assert_eq!(*rec.source.as_ref().unwrap(), System);
        assert!(rec.is_sys());
        assert!(!rec.is_ancillary());

        let rec = Rec::new_from(t.clone(), Ancillary);
        assert_eq!(*rec.source.as_ref().unwrap(), Ancillary);
        assert!(!rec.is_sys());
        assert!(rec.is_ancillary());
    }

    #[test]
    fn rec_source() {
        let t: Trust = Trust::new("/foo", 1, "0x00");

        assert!(!Rec::new(t.clone()).is_ancillary());
        assert!(!Rec::new(t.clone()).is_sys());

        assert!(Rec::new_from(t.clone(), Ancillary).is_ancillary());
        assert!(Rec::new_from(t, System).is_sys());
    }
}
