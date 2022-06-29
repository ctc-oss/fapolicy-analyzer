/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::collections::btree_map::Iter;
use std::collections::{BTreeMap, HashMap};
use std::fmt::{Display, Formatter};

use crate::Rule;

/// Rule Definition
/// Can be valid or invalid
/// When invalid it provides the text definition
/// When valid the text definition can be rendered from the ADTs
#[derive(Clone, Debug)]
pub enum RuleDef {
    Valid(Rule),
    ValidWithWarning(Rule, String),
    Invalid { text: String, error: String },
}

impl Display for RuleDef {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let txt = match self {
            RuleDef::Valid(r) | RuleDef::ValidWithWarning(r, _) => r.to_string(),
            RuleDef::Invalid { text, .. } => text.clone(),
        };
        f.write_fmt(format_args!("{}", txt))
    }
}

/// Rules Database
/// A container for rules and their metadata
#[derive(Clone, Debug, Default)]
pub struct DB {
    lookup: BTreeMap<usize, RuleDef>,
    source: HashMap<usize, String>,
}

impl From<Vec<RuleDef>> for DB {
    fn from(src: Vec<RuleDef>) -> Self {
        let lookup: BTreeMap<usize, RuleDef> = src
            .iter()
            .enumerate()
            // fapolicyd rules are 1-based index
            .map(|(k, v)| (k + 1, v.clone()))
            .collect();
        DB {
            lookup,
            ..DB::default()
        }
    }
}

impl DB {
    /// Construct DB using the provided RuleDefs from the single source
    pub fn from_source(source: String, defs: Vec<RuleDef>) -> Self {
        DB::from_sources(defs.into_iter().map(|d| (source.clone(), d)).collect())
    }

    /// Construct DB using the provided RuleDefs and associated sources
    pub fn from_sources(defs: Vec<(String, RuleDef)>) -> Self {
        let default: Self = defs
            .clone()
            .into_iter()
            .map(|(_, d)| d)
            .collect::<Vec<RuleDef>>()
            .into();
        Self {
            lookup: default.lookup,
            source: defs
                .iter()
                .enumerate()
                // fapolicyd rules are 1-based index
                .map(|(k, (s, _))| (k + 1, s.clone()))
                .collect(),
        }
    }

    /// Get an iterator to RuleDefs
    pub fn iter(&self) -> Iter<'_, usize, RuleDef> {
        self.lookup.iter()
    }

    /// Get a Vec of RuleDefs
    pub fn values(&self) -> Vec<&RuleDef> {
        self.lookup.values().collect()
    }

    /// Get the number of RuleDefs
    pub fn len(&self) -> usize {
        self.lookup.len()
    }

    /// Test if there are any RuleDefs in this DB
    pub fn is_empty(&self) -> bool {
        self.lookup.is_empty()
    }

    /// Get a RuleDef by ID
    pub fn get(&self, id: usize) -> Option<&RuleDef> {
        self.lookup.get(&id)
    }

    /// Get the source of a RuleDef by ID
    pub fn source(&self, id: usize) -> Option<String> {
        self.source.get(&id).cloned()
    }
}

#[cfg(test)]
mod tests {
    use crate::{Decision, Object, Permission, Subject};

    use super::*;

    impl From<Rule> for RuleDef {
        fn from(r: Rule) -> Self {
            RuleDef::Valid(r)
        }
    }

    fn any_all_all(decision: Decision) -> RuleDef {
        Rule::new(Subject::all(), Permission::Any, Object::all(), decision).into()
    }

    impl RuleDef {
        pub fn unwrap(&self) -> Rule {
            match self {
                RuleDef::Valid(val) => val.clone(),
                RuleDef::ValidWithWarning(val, _) => val.clone(),
                RuleDef::Invalid { text: _, error: _ } => {
                    panic!("called `RuleDef::unwrap()` on an invalid rule")
                }
            }
        }
    }

    #[test]
    fn default_db_is_empty() {
        assert!(DB::default().is_empty());
    }

    #[test]
    fn db_create() {
        let r1: RuleDef = Rule::new(
            Subject::all(),
            Permission::Any,
            Object::all(),
            Decision::Allow,
        )
        .into();
        let db: DB = vec![r1].into();
        assert!(!db.is_empty());
        assert!(db.get(1).is_some());
    }

    #[test]
    fn db_create_single_source() {
        let r1 = any_all_all(Decision::Allow);
        let r2 = any_all_all(Decision::Deny);

        let source = "/foo/bar.rules";
        let db: DB = DB::from_source(source.to_string(), vec![r1, r2]);
        assert_eq!(db.source.get(&1).unwrap(), source);
        assert_eq!(db.source.get(&2).unwrap(), source);
    }

    #[test]
    fn db_create_each_source() {
        let r1 = any_all_all(Decision::Allow);
        let r2 = any_all_all(Decision::Deny);

        let source1 = "/foo.rules";
        let source2 = "/bar.rules";
        let db: DB = DB::from_sources(vec![(source1.to_string(), r1), (source2.to_string(), r2)]);
        assert_eq!(db.source.get(&1).unwrap(), source1);
        assert_eq!(db.source.get(&2).unwrap(), source2);
    }

    #[test]
    fn maintain_order() {
        let subjs = vec!["fee", "fi", "fo", "fum", "this", "is", "such", "fun"];
        let rules: Vec<RuleDef> = subjs
            .iter()
            .map(|s| {
                Rule::new(
                    Subject::from_exe(s),
                    Permission::Any,
                    Object::all(),
                    Decision::Allow,
                )
                .into()
            })
            .collect();

        let db: DB = rules.into();
        assert!(!db.is_empty());
        assert_eq!(db.len(), 8);

        for s in subjs.iter().enumerate() {
            assert_eq!(db.get(s.0 + 1).unwrap().unwrap().subj.exe().unwrap(), *s.1);
        }
    }
}
