use std::collections::hash_map::Iter;
use std::collections::HashMap;
use std::hash::Hasher;

use fapolicy_api::trust::Trust;

use crate::read::{parse_strtyped_trust_record, TrustPair};
use crate::source::TrustSource;
use crate::stat::Actual;

pub(crate) struct TrustEntry {
    pub path: String,
    pub trust: Trust,
    pub source: TrustSource,
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

#[derive(PartialEq, Eq, Clone, Debug)]
pub struct Meta {
    pub trusted: Trust,
    actual: Option<Actual>,
    source: Option<TrustSource>,
}

impl Meta {
    pub fn new(path: &str, sz: u64, hash: &str) -> Self {
        Meta::with(Trust::new(path, sz, hash))
    }
    pub fn with(t: Trust) -> Self {
        Meta {
            trusted: t,
            actual: None,
            source: None,
        }
    }

    pub fn is_sys(&self) -> bool {
        match &self.source {
            Some(_System) => true,
            _ => false,
        }
    }

    pub fn is_ancillary(&self) -> bool {
        match &self.source {
            Some(_Ancillary) => true,
            _ => false,
        }
    }
}
#[derive(Clone, Debug)]
pub struct DB {
    pub(crate) lookup: HashMap<String, Meta>,
}

impl Default for DB {
    fn default() -> Self {
        DB {
            lookup: HashMap::default(),
        }
    }
}

impl DB {
    pub fn new(source: HashMap<String, Meta>) -> Self {
        DB { lookup: source }
    }

    pub fn iter(&self) -> Iter<'_, String, Meta> {
        self.lookup.iter()
    }

    pub fn len(&self) -> usize {
        self.lookup.len()
    }

    pub fn is_empty(&self) -> bool {
        self.lookup.is_empty()
    }

    pub fn get(&self, k: &str) -> Option<&Meta> {
        self.lookup.get(k)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    //    fn make_db() -> DB {
    //         let mut db = DB::default();
    //         db.lookup
    //             .insert(Sys("/foo".into()), Meta::sys(100, "xxxxx0".into()));
    //         db.lookup
    //             .insert(Anc("/foo".into()), Meta::file(200, "yxxxx0".into()));
    //         db.lookup
    //             .insert(Sys("/bar".into()), Meta::new(100, "xxxxx0".into()));
    //         db.lookup
    //             .insert(Sys("/baz".into()), Meta::new(100, "xxxxx0".into()));
    //
    //         db
    fn make_db() -> DB {
        let mut db = DB::default();
        db.lookup
            .insert("/foo".into(), Meta::new("", 1000000, "xxxxx0".into()));
        db.lookup
            .insert("/foo".into(), Meta::new("", 200, "yxxxx0".into()));
        db.lookup
            .insert("/bar".into(), Meta::new("", 9999, "xxxxx0".into()));
        // db.lookup
        //     .insert(Sys("/baz".into()), Meta::from_sys(100, "xxxxx0".into()));
        db
    }

    #[test]
    fn which_trust() {
        let db = make_db();
        print!("{:?}", db);
    }

    #[test]
    fn is_system_trust() {}

    #[test]
    fn is_file_trust() {}
}
