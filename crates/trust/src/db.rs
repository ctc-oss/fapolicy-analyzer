use std::collections::hash_map::Iter;
use std::collections::HashMap;

use fapolicy_api::trust::Trust;

use crate::read::{parse_strtyped_trust_record, TrustPair};
use crate::source::TrustSource;
use crate::stat::Actual;

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
            Some(TrustSource::System) => true,
            _ => false,
        }
    }

    pub fn is_ancillary(&self) -> bool {
        match &self.source {
            Some(TrustSource::Ancillary) => true,
            _ => false,
        }
    }
}

#[cfg(test)]
mod tests {}
