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

use Entry::*;

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

#[derive(Clone, Debug)]
pub struct CommentEntry {
    pub text: String,
    pub origin: Origin,
    _fk: usize,
}

/// Rule Definition
/// Can be valid or invalid
/// When invalid it provides the text definition
/// When valid the text definition can be rendered from the ADTs
#[derive(Clone, Debug)]
pub enum Entry {
    // rules
    ValidRule(Rule),
    RuleWithWarning(Rule, String),
    Invalid { text: String, error: String },

    // sets
    ValidSet(Set),
    SetWithWarning(Set, String),
    InvalidSet { text: String, error: String },

    // other
    Comment(String),
}

impl Display for Entry {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let txt = match self {
            ValidRule(r) | RuleWithWarning(r, _) => r.to_string(),
            ValidSet(r) | SetWithWarning(r, _) => r.to_string(),
            Invalid { text, .. } => text.clone(),
            InvalidSet { text, .. } => text.clone(),
            Comment(text) => format!("#{}", text),
        };
        f.write_fmt(format_args!("{}", txt))
    }
}

impl Entry {
    fn diagnostic_messages(&self) -> Option<String> {
        match self {
            RuleWithWarning(_, w) | SetWithWarning(_, w) => Some(w.clone()),
            Invalid { error, .. } | InvalidSet { error, .. } => Some(error.clone()),
            _ => None,
        }
    }
}

fn is_valid(def: &Entry) -> bool {
    !matches!(def, Invalid { .. } | InvalidSet { .. })
}

fn is_rule(def: &Entry) -> bool {
    matches!(def, ValidRule(_) | RuleWithWarning(..) | Invalid { .. })
}

fn is_set(def: &Entry) -> bool {
    matches!(def, ValidSet(_) | SetWithWarning(..) | InvalidSet { .. })
}

fn is_comment(def: &Entry) -> bool {
    matches!(def, Comment(_))
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
    comments: BTreeMap<usize, CommentEntry>,
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
                msg: e.diagnostic_messages(),
                _fk: *fk,
            })
            .map(|e| (e.id, e))
            .collect();

        let sets: BTreeMap<usize, SetEntry> = model
            .iter()
            .enumerate()
            .map(|(fk, v)| (v, fk))
            .filter(|((_, (_, m)), _)| is_set(m))
            .map(|((id, (o, e)), fk)| {
                (
                    *id,
                    SetEntry {
                        // todo;; extract the set name
                        name: "_".to_string(),
                        text: e.to_string(),
                        origin: o.clone(),
                        valid: is_valid(e),
                        msg: e.diagnostic_messages(),
                        _fk: fk,
                    },
                )
            })
            .collect();

        let comments = model
            .iter()
            .enumerate()
            .map(|(fk, v)| (v, fk))
            .filter(|((_, (_, m)), _)| is_comment(m))
            .map(|((id, (o, e)), fk)| {
                (
                    *id,
                    CommentEntry {
                        text: e.to_string(),
                        origin: o.clone(),
                        _fk: fk,
                    },
                )
            })
            .collect();

        Self {
            model,
            rules,
            sets,
            comments,
        }
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

    /// Get a RuleEntry ref by FK
    pub fn rule_rev(&self, fk: usize) -> Option<&RuleEntry> {
        self.rules.iter().find(|(_, e)| e._fk == fk).map(|(_, e)| e)
    }

    /// Get a vec of all RuleEntry refs
    pub fn rules(&self) -> Vec<&RuleEntry> {
        self.rules.values().collect()
    }

    /// Get a vec of all SetEntry refs
    pub fn sets(&self) -> Vec<&SetEntry> {
        self.sets.values().collect()
    }

    /// Get a vec of all CommentEntry refs
    pub fn comments(&self) -> Vec<&CommentEntry> {
        self.comments.values().collect()
    }

    pub fn entry(&self, num: usize) -> Option<&Entry> {
        self.model.get(&num).map(|(_, e)| e)
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
            ValidRule(r)
        }
    }

    impl DB {
        fn from_source(origin: Origin, defs: Vec<Entry>) -> Self {
            DB::from_sources(defs.into_iter().map(|d| (origin.clone(), d)).collect())
        }
    }

    impl Entry {
        pub fn unwrap(&self) -> Rule {
            match self {
                ValidRule(val) => val.clone(),
                RuleWithWarning(val, _) => val.clone(),
                _ => {
                    panic!("called unwrap on an invalid rule or set def")
                }
            }
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

        for s in subjs.iter().enumerate() {
            assert_eq!(db.entry(s.0).unwrap().unwrap().subj.exe().unwrap(), *s.1);
        }
    }

    #[test]
    fn test_prefixed_comment() {
        assert!(Comment("sometext".to_string()).to_string().starts_with('#'))
    }
}
