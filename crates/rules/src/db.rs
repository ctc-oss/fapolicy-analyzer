/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::collections::btree_map::Iter;
use std::collections::BTreeMap;
use std::fmt::{Display, Formatter};

use crate::{Rule, Set};

#[derive(Clone, Debug)]
pub struct RuleEntry {
    pub id: usize,
    pub text: String,
    pub origin: Origin,
    pub valid: bool,
    pub msg: Option<String>,
    _fk: usize,
}

#[derive(Clone, Debug)]
pub struct SetEntry {
    pub name: String,
    pub text: String,
    pub origin: Origin,
    pub valid: bool,
    pub msg: Option<String>,
    _fk: usize,
}

/// Rule Definition
/// Can be valid or invalid
/// When invalid it provides the text definition
/// When valid the text definition can be rendered from the ADTs
#[derive(Clone, Debug)]
pub enum Entry {
    ValidRule(Rule),
    ValidSet(Set),
    RuleWithWarning(Rule, String),
    SetWithWarning(Set, String),
    Invalid { text: String, error: String },
    InvalidSet { text: String, error: String },
}

impl Display for Entry {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let txt = match self {
            Entry::ValidRule(r) | Entry::RuleWithWarning(r, _) => r.to_string(),
            Entry::ValidSet(r) | Entry::SetWithWarning(r, _) => r.to_string(),
            Entry::Invalid { text, .. } => text.clone(),
            Entry::InvalidSet { text, .. } => text.clone(),
        };
        f.write_fmt(format_args!("{}", txt))
    }
}

impl Entry {
    // todo;; rename to diagnostics
    fn warnings(&self) -> Option<String> {
        match self {
            Entry::RuleWithWarning(_, w) | Entry::SetWithWarning(_, w) => Some(w.clone()),
            Entry::Invalid { error, .. } | Entry::InvalidSet { error, .. } => Some(error.clone()),
            _ => None,
        }
    }
}

fn is_valid(def: &Entry) -> bool {
    !matches!(def, Entry::Invalid { .. } | Entry::InvalidSet { .. })
}

fn is_rule(def: &Entry) -> bool {
    !matches!(
        def,
        Entry::ValidSet(_) | Entry::SetWithWarning(..) | Entry::InvalidSet { .. }
    )
}

type Origin = String;
type DbEntry = (Origin, Entry);

/// Rules Database
/// A container for rules and their metadata
#[derive(Clone, Debug, Default)]
pub struct DB {
    model: BTreeMap<usize, DbEntry>,
    rules: BTreeMap<usize, RuleEntry>,
    sets: BTreeMap<usize, SetEntry>,
}

impl From<Vec<(Origin, Entry)>> for DB {
    fn from(s: Vec<(String, Entry)>) -> Self {
        DB::from_sources(s)
    }
}

impl DB {
    /// Construct DB using the provided RuleDefs and associated sources
    pub(crate) fn from_sources(defs: Vec<(Origin, Entry)>) -> Self {
        let model: BTreeMap<usize, DbEntry> = defs
            .into_iter()
            .enumerate()
            .map(|(i, (source, d))| (i, (source, d)))
            .collect();

        let rules: BTreeMap<usize, RuleEntry> = model
            .iter()
            .filter(|(_fk, (_, e))| is_rule(e))
            .enumerate()
            .map(|(id, (fk, (o, e)))| RuleEntry {
                id: id + 1,
                text: e.to_string(),
                origin: o.clone(),
                valid: is_valid(e),
                msg: e.warnings(),
                _fk: *fk,
            })
            .map(|e| (e.id, e))
            .collect();

        let sets: BTreeMap<usize, SetEntry> = model
            .iter()
            .enumerate()
            .map(|(fk, v)| (v, fk))
            .filter(|((_, (_, m)), _)| !is_rule(m))
            .map(|((id, (o, r)), fk)| {
                (
                    *id,
                    SetEntry {
                        // todo;; extract the set name
                        name: "_".to_string(),
                        text: r.to_string(),
                        origin: o.clone(),
                        valid: is_valid(r),
                        msg: r.warnings(),
                        _fk: fk,
                    },
                )
            })
            .collect();

        Self { model, rules, sets }
    }

    /// Get the number of RuleDefs
    pub fn len(&self) -> usize {
        self.model.len()
    }

    /// Test if there are any RuleDefs in this DB
    pub fn is_empty(&self) -> bool {
        self.model.is_empty()
    }

    /// Get a RuleEntry ref by ID
    pub fn rule(&self, num: usize) -> Option<&RuleEntry> {
        self.rules.get(&num)
    }

    /// Get a vec of all RuleEntry refs
    pub fn rules(&self) -> Vec<&RuleEntry> {
        self.rules.values().collect()
    }

    /// Get a vec of all SetEntry refs
    pub fn sets(&self) -> Vec<&SetEntry> {
        self.sets.values().collect()
    }

    /// Get a model iterator
    pub fn iter(&self) -> Iter<'_, usize, DbEntry> {
        self.model.iter()
    }
}

#[cfg(test)]
mod tests {
    use crate::{Decision, Object, Permission, Subject};

    use super::*;

    impl From<Rule> for Entry {
        fn from(r: Rule) -> Self {
            Entry::ValidRule(r)
        }
    }

    impl DB {
        fn from_source(origin: Origin, defs: Vec<Entry>) -> Self {
            DB::from_sources(defs.into_iter().map(|d| (origin.clone(), d)).collect())
        }
    }

    fn any_all_all(decision: Decision) -> Entry {
        Rule::new(Subject::all(), Permission::Any, Object::all(), decision).into()
    }

    #[test]
    fn default_db_is_empty() {
        assert!(DB::default().is_empty());
    }

    #[test]
    fn db_create() {
        let r1: Entry = Rule::new(
            Subject::all(),
            Permission::Any,
            Object::all(),
            Decision::Allow,
        )
        .into();
        let source = "foo.rules".to_string();
        let db: DB = vec![(source, r1)].into();
        assert!(!db.is_empty());
        assert!(db.rule(1).is_some());
    }

    #[test]
    fn db_create_single_source() {
        let r1 = any_all_all(Decision::Allow);
        let r2 = any_all_all(Decision::Deny);

        let source = "/foo/bar.rules";
        let db: DB = DB::from_source(source.to_string(), vec![r1, r2]);
        assert_eq!(db.rule(1).unwrap().origin, source);
        assert_eq!(db.rule(2).unwrap().origin, source);
    }

    #[test]
    fn db_create_each_source() {
        let r1 = any_all_all(Decision::Allow);
        let r2 = any_all_all(Decision::Deny);

        let source1 = "/foo.rules";
        let source2 = "/bar.rules";
        let db: DB = DB::from_sources(vec![(source1.to_string(), r1), (source2.to_string(), r2)]);
        assert_eq!(db.rule(1).unwrap().origin, source1);
        assert_eq!(db.rule(2).unwrap().origin, source2);
    }

    #[test]
    fn maintain_order() {
        let source = "foo.rules".to_string();
        let subjs = vec!["fee", "fi", "fo", "fum", "this", "is", "such", "fun"];
        let rules: Vec<(String, Entry)> = subjs
            .iter()
            .map(|s| {
                (
                    source.clone(),
                    Rule::new(
                        Subject::from_exe(s),
                        Permission::Any,
                        Object::all(),
                        Decision::Allow,
                    )
                    .into(),
                )
            })
            .collect();

        let db: DB = rules.into();
        assert!(!db.is_empty());
        assert_eq!(db.len(), 8);

        // todo;; the accessor of the parsed rules was lost....
        // for s in subjs.iter().enumerate() {
        //     assert_eq!(db.rule(s.0 + 1).unwrap().unwrap().subj.exe().unwrap(), *s.1);
        // }
    }
}
