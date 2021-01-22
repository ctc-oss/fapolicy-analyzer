use std::fs::File;
use std::io::{prelude::*, BufReader};
use std::str::FromStr;

pub struct TrustEntry {
    pub path: String,
    /* size is an off_t */
    pub size: i64,
    pub hash: String,
}

impl FromStr for TrustEntry {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let xx: Vec<&str> = s.split(' ').collect();
        match xx.as_slice() {
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
    path: String,
    entries: Vec<TrustEntry>,
}

impl FileTrustDB {
    pub fn new(p: &String) -> FileTrustDB {
        FileTrustDB {
            path: p.clone(),
            entries: vec![],
        }
    }

    pub fn from(p: &String) -> FileTrustDB {
        let v = Self::read_entries(&p);
        FileTrustDB {
            path: p.clone(),
            entries: v,
        }
    }

    pub fn entries(self: FileTrustDB) -> Vec<TrustEntry> {
        self.entries
    }

    fn read_entries(path: &String) -> Vec<TrustEntry> {
        let f = File::open(path).unwrap();
        let r = BufReader::new(f);

        r.lines()
            .map(|r| r.unwrap())
            .filter(|s| !s.is_empty() && !s.starts_with("#"))
            .map(|l| TrustEntry::from_str(&l).unwrap())
            .collect()
    }
}
