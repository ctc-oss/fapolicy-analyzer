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

impl DB {
    pub fn new(source: HashMap<String, Rec>) -> Self {
        DB { lookup: source }
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
}

#[derive(PartialEq, Eq, Clone, Debug)]
pub struct Rec {
    pub trusted: Trust,
    actual: Option<Actual>,
    source: Option<TrustSource>,
}

impl Rec {
    pub fn new(path: &str, sz: u64, hash: &str) -> Self {
        Rec::new_from_source(Trust::new(path, sz, hash), TrustSource::Ancillary)
    }

    pub fn new_from(t: Trust) -> Self {
        Rec {
            trusted: t,
            actual: None,
            source: None,
        }
    }

    pub(crate) fn new_from_source(t: Trust, source: TrustSource) -> Self {
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
mod tests {}
