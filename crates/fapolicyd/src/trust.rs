use std::fs::File;
use std::io::{prelude::*, BufReader};
use std::str::FromStr;

#[derive(Clone)]
pub struct TrustEntry {
    pub path: String,
    /* size is an off_t */
    pub size: i64,
    pub hash: String,
}

impl TrustEntry {
    pub fn new(path: &str, size: i64, hash: &str) -> TrustEntry {
        TrustEntry {
            path: path.to_string(),
            size,
            hash: hash.to_string(),
        }
    }
}

impl FromStr for TrustEntry {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let v: Vec<&str> = s.split(' ').collect();
        match v.as_slice() {
            [f, sz, sha] => Ok(TrustEntry {
                path: f.to_string(),
                size: sz.parse().unwrap(),
                hash: sha.to_string(),
            }),
            _ => Err(String::from("failed to read record")),
        }
    }
}

pub struct FileTrustDB {
    pub path: String,
    entries: Vec<TrustEntry>,
}

impl FileTrustDB {
    pub fn new(p: &str) -> FileTrustDB {
        FileTrustDB::from(p)
    }

    pub fn from(p: &str) -> FileTrustDB {
        let entries = Self::read_entries(&p);
        FileTrustDB {
            path: String::from(p),
            entries,
        }
    }

    pub fn entries(self: FileTrustDB) -> Vec<TrustEntry> {
        self.entries
    }

    fn read_entries(path: &str) -> Vec<TrustEntry> {
        let f = File::open(path).unwrap();
        let r = BufReader::new(f);

        r.lines()
            .map(|r| r.unwrap())
            .filter(|s| !s.is_empty() && !s.starts_with('#'))
            .map(|l| TrustEntry::from_str(&l).unwrap())
            .collect()
    }
}
