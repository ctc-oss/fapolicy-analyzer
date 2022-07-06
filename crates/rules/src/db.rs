/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fmt::{Display, Formatter};

use crate::{Rule, Set};

#[derive(Clone, Debug)]
pub struct RuleEntry {
    pub id: usize,
    pub text: String,
    pub origin: String,
    pub valid: bool,
    pub msg: Option<String>,
}

#[derive(Clone, Debug)]
pub struct SetEntry {
    pub text: String,
    pub origin: String,
    pub valid: bool,
    pub msg: String,
}

/// Rule Definition
/// Can be valid or invalid
/// When invalid it provides the text definition
/// When valid the text definition can be rendered from the ADTs
#[derive(Clone, Debug)]
pub(crate) enum RuleDef {
    Valid(Rule),
    ValidWithWarning(Rule, String),
    ValidSet(Set),
    ValidSetWithWarning(Set, String),
    Invalid { text: String, error: String },
}

impl Display for RuleDef {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let txt = match self {
            RuleDef::Valid(r) | RuleDef::ValidWithWarning(r, _) => r.to_string(),
            RuleDef::ValidSet(r) | RuleDef::ValidSetWithWarning(r, _) => r.to_string(),
            RuleDef::Invalid { text, .. } => text.clone(),
        };
        f.write_fmt(format_args!("{}", txt))
    }
}

impl RuleDef {
    fn is_valid(&self) -> bool {
        match self {
            RuleDef::Invalid { .. } => false,
            _ => true,
        }
    }

    fn is_rule(&self) -> bool {
        match self {
            RuleDef::ValidSet(_) | RuleDef::ValidSetWithWarning(_, _) => false,
            _ => true,
        }
    }

    fn warnings(&self) -> Option<String> {
        match self {
            RuleDef::ValidWithWarning(_, w) | RuleDef::ValidSetWithWarning(_, w) => Some(w.clone()),
            _ => None,
        }
    }
}

type DbEntry = (String, RuleDef);
type DbTriple = (RuleDef, String, usize);

/// Rules Database
/// A container for rules and their metadata
#[derive(Clone, Debug, Default)]
pub struct DB {
    model: Vec<DbEntry>,
    raw: Option<String>,
}

impl From<Vec<(String, RuleDef)>> for DB {
    // from vec of Origin, Def
    fn from(src: Vec<(String, RuleDef)>) -> Self {
        DB {
            model: src,
            ..DB::default()
        }
    }
}

impl DB {
    /// Construct DB using the provided RuleDefs from the single source
    fn from_source(source: String, defs: Vec<RuleDef>) -> Self {
        DB::from_sources(defs.into_iter().map(|d| (source.clone(), d)).collect())
    }

    /// Construct DB using the provided RuleDefs and associated sources
    pub(crate) fn from_sources(defs: Vec<(String, RuleDef)>) -> Self {
        Self {
            model: defs,
            ..Default::default()
        }
    }

    // id, rule, origin
    pub fn rules(&self) -> Vec<RuleEntry> {
        self.model
            .iter()
            .enumerate()
            .filter(|(_, (_, m))| m.is_rule())
            .map(|(id, (o, r))| RuleEntry {
                id,
                text: r.to_string(),
                origin: o.clone(),
                valid: r.is_valid(),
                msg: r.warnings(),
            })
            .collect()
    }

    /// Get the number of RuleDefs
    pub fn len(&self) -> usize {
        self.model.len()
    }

    /// Test if there are any RuleDefs in this DB
    pub fn is_empty(&self) -> bool {
        self.model.is_empty()
    }

    /// Get a RuleDef by ID
    pub fn rule(&self, num: usize) -> Option<RuleEntry> {
        self.model
            .iter()
            .filter(|(_, e)| e.is_rule())
            .enumerate()
            .find(|(id, _)| *id + 1 == num)
            .map(|(id, (o, r))| RuleEntry {
                id,
                text: r.to_string(),
                origin: o.clone(),
                valid: r.is_valid(),
                msg: r.warnings(),
            })
    }

    pub(crate) fn defs(&self) -> Vec<DbTriple> {
        self.model
            .iter()
            .enumerate()
            .filter(|(_, (_, m))| m.is_rule())
            .map(|(id, (o, r))| (r.clone(), o.clone(), id + 1))
            .collect()
    }

    fn origin(&self, num: usize) -> Option<String> {
        self.defs()
            .iter()
            .find(|(_, _, id)| *id == num)
            .map(|(_, o, _)| o.clone())
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
                _ => {
                    panic!("called `RuleDef::unwrap()` on an invalid rule or set def")
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
        println!("{db:?}");
        assert_eq!(db.origin(1).unwrap(), source);
        assert_eq!(db.origin(2).unwrap(), source);
    }

    #[test]
    fn db_create_each_source() {
        let r1 = any_all_all(Decision::Allow);
        let r2 = any_all_all(Decision::Deny);

        let source1 = "/foo.rules";
        let source2 = "/bar.rules";
        let db: DB = DB::from_sources(vec![(source1.to_string(), r1), (source2.to_string(), r2)]);
        assert_eq!(db.origin(1).unwrap(), source1);
        assert_eq!(db.origin(2).unwrap(), source2);
    }

    #[test]
    fn maintain_order() {
        let source = "foo.rules".to_string();
        let subjs = vec!["fee", "fi", "fo", "fum", "this", "is", "such", "fun"];
        let rules: Vec<(String, RuleDef)> = subjs
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
