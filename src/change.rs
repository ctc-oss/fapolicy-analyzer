use std::collections::HashMap;

use crate::api::{Trust, TrustSource};
use crate::change::TrustChangeErr::NotFound;
use crate::sha::sha256_digest;
use std::fs::File;
use std::io::BufReader;

#[derive(Clone, Debug)]
pub struct TrustSet {
    trust: HashMap<String, Trust>,
}

pub enum TrustChangeErr {
    NotFound,
}

impl TrustSet {
    pub fn empty() -> Self {
        TrustSet {
            trust: HashMap::new(),
        }
    }

    pub fn from(init: Vec<Trust>) -> Self {
        TrustSet {
            trust: init
                .iter()
                .map(|t| (t.path.to_string(), t.clone()))
                .collect(),
        }
    }

    pub fn add(&mut self, path: &str) -> Result<(), TrustChangeErr> {
        match new_trust_record(path) {
            Ok(t) => {
                self.trust.insert(path.to_string(), t);
                Ok(())
            }
            Err(_) => Ok(()),
        }
    }
    pub fn del(&mut self, path: &str) -> Result<(), TrustChangeErr> {
        match self.trust.remove(path) {
            Some(_) => Ok(()),
            None => Err(NotFound),
        }
    }

    pub fn len(&self) -> usize {
        self.trust.len()
    }
}

fn new_trust_record(path: &str) -> Result<Trust, String> {
    let f = File::open(path).unwrap();
    let sha = sha256_digest(BufReader::new(&f)).unwrap();

    Ok(Trust {
        path: path.to_string(),
        size: f.metadata().unwrap().len(),
        hash: sha,
        source: TrustSource::Ancillary,
    })
}
