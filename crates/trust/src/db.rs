use crate::read::{parse_strtyped_trust_record, TrustPair};
use crate::source::TrustSource;
use fapolicy_api::trust::Trust;
use std::collections::HashMap;
use std::hash::{Hash, Hasher};

#[derive(Debug)]
struct T {
    size: u64,
    hash: String,
}
#[derive(Debug)]
struct A {
    size: u64,
    hash: String,
    last_mod: String,
}

#[derive(Debug)]
pub struct TrustRec {
    pub path: String,
    source: TrustSource,
}

pub struct TrustEntry {
    pub k: TrustRec,
    pub v: Trust,
}

impl From<TrustPair> for TrustEntry {
    fn from(kv: TrustPair) -> Self {
        let (tt, v) = kv.v.split_once(' ').unwrap();
        let (t, s) = parse_strtyped_trust_record(format!("{} {}", kv.k, v).as_str(), tt)
            .expect("failed to parse_strtyped_trust_record");

        TrustEntry {
            k: TrustRec {
                path: t.path.clone(),
                source: s,
            },
            v: t,
        }
    }
}

impl TrustRec {
    fn file(path: String) -> Self {
        TrustRec::new(path, TrustSource::Ancillary)
    }
    fn sys(path: String) -> Self {
        TrustRec::new(path, TrustSource::System)
    }
    fn new(path: String, source: TrustSource) -> Self {
        TrustRec { path, source }
    }
    fn is_sys(&self) -> bool {
        self.source == TrustSource::System
    }

    fn is_ancillary(&self) -> bool {
        self.source == TrustSource::Ancillary
    }
}

impl Eq for TrustRec {}

impl PartialEq for TrustRec {
    fn eq(&self, other: &Self) -> bool {
        self.path == other.path
    }
}

impl Hash for TrustRec {
    fn hash<H: Hasher>(&self, hasher: &mut H) {
        self.path.hash(hasher);
    }
}

#[derive(Debug)]
struct Meta {
    trusted: T,
    actual: Option<A>,
}

impl Meta {
    fn new(sz: u64, hash: String) -> Self {
        Meta {
            trusted: T {
                size: sz,
                hash: hash.into(),
            },
            actual: None,
        }
    }
}
#[derive(Debug)]
struct DB {
    lookup: HashMap<TrustRec, Meta>,
}

impl Default for DB {
    fn default() -> Self {
        DB {
            lookup: HashMap::default(),
        }
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
        db.lookup.insert(
            TrustRec::sys("/foo".into()),
            Meta::new(1000000, "xxxxx0".into()),
        );
        db.lookup.insert(
            TrustRec::file("/foo".into()),
            Meta::new(200, "yxxxx0".into()),
        );
        db.lookup.insert(
            TrustRec::sys("/bar".into()),
            Meta::new(9999, "xxxxx0".into()),
        );
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
