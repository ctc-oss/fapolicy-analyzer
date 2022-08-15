/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::db::{Entry, DB};
use crate::linter::findings::*;
use crate::Rule;

type LintFn = fn(usize, &Rule, &DB) -> Option<String>;

pub fn lint_db(db: DB) -> DB {
    let lints: Vec<LintFn> = vec![
        l001,
        l002_subject_path_missing,
        l003_object_path_missing,
        l004_duplicate_rule,
        l005_object_dir_missing_trailing_slash,
    ];

    db.iter()
        .map(|(&fk, (source, def))| match def {
            Entry::ValidRule(r) => {
                let x: Vec<String> = lints.iter().filter_map(|f| f(fk, r, &db)).collect();
                if x.is_empty() {
                    (source.clone(), Entry::ValidRule(r.clone()))
                } else {
                    (
                        source.clone(),
                        Entry::RuleWithWarning(r.clone(), x.first().unwrap().clone()),
                    )
                }
            }
            other => (source.clone(), other.clone()),
        })
        .collect::<Vec<(String, Entry)>>()
        .into()
}

#[cfg(test)]
mod tests {
    use crate::linter::findings::L001_MESSAGE;
    use crate::read::deserialize_rules_db;
    use std::error::Error;

    #[test]
    fn lint_short_circuit_none() -> Result<(), Box<dyn Error>> {
        let db = deserialize_rules_db(
            r#"
        [foo.bar]
        allow perm=any all : all
        "#,
        )?;
        let r = db.rule(1).unwrap();
        assert!(r.msg.is_none());
        Ok(())
    }

    #[test]
    fn lint_short_circuit_none2() -> Result<(), Box<dyn Error>> {
        let db = deserialize_rules_db(
            r#"
        [foo.bar]
        allow perm=any all : all
        %foo=bar
        "#,
        )?;
        let r = db.rule(1).unwrap();
        assert!(r.msg.is_none());
        Ok(())
    }

    #[test]
    fn lint_short_circuit_findings() -> Result<(), Box<dyn Error>> {
        let db = deserialize_rules_db(
            r#"
        [foo.bar]
        allow perm=any all : all
        allow perm=any all : all
        "#,
        )?;
        let r = db.rule(1).unwrap();
        assert!(r.msg.is_some());
        assert_eq!(r.msg.as_ref().unwrap(), L001_MESSAGE);
        Ok(())
    }
}
