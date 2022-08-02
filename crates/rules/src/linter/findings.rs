/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::db::{Entry, DB};
use crate::object::Part;
use crate::Rule;
use std::path::PathBuf;

pub(crate) const L001_MESSAGE: &str = "Using any+all+all here will short-circuit all other rules.";
pub(crate) const L004_MESSAGE: &str = "Duplicate of rule";

pub fn l001(fk: usize, r: &Rule, db: &DB) -> Option<String> {
    let id = db.rule_rev(fk).map(|e| e.id).unwrap();
    if id < db.rules().len() // rules are indexed from 1
        && r.perm.is_any()
        && r.subj.is_all()
        && r.obj.is_all()
    {
        Some(L001_MESSAGE.to_string())
    } else {
        None
    }
}

pub fn l002_subject_path_missing(_: usize, r: &Rule, _db: &DB) -> Option<String> {
    if let Some(path) = r.subj.exe().map(PathBuf::from) {
        if !path.exists() {
            Some("The exe specified does not exist.".to_string())
        } else {
            None
        }
    } else {
        None
    }
}

fn is_missing(p: &str) -> bool {
    !PathBuf::from(p).exists()
}

fn path_does_not_exist_message(t: &str) -> String {
    format!("The {} specified does not exist.", t)
}

pub fn l003_object_path_missing(_: usize, r: &Rule, _db: &DB) -> Option<String> {
    r.obj
        .parts
        .iter()
        .filter_map(|p| match p {
            Part::Device(p) if is_missing(p) => Some(path_does_not_exist_message("device")),
            Part::Dir(p) if is_missing(p) => Some(path_does_not_exist_message("directory")),
            Part::Path(p) if is_missing(p) => Some(path_does_not_exist_message("path")),
            _ => None,
        })
        .collect::<Vec<String>>()
        .first()
        .cloned()
}

pub fn l004_duplicate_rule(fk: usize, r: &Rule, db: &DB) -> Option<String> {
    db.iter()
        .filter_map(|(&fk2, (_, e))| match e {
            Entry::ValidRule(other) if fk != fk2 && other == r => {
                let dupe = db.rule_rev(fk2).map(|e| e.id).unwrap();
                Some(format!("{} {}", L004_MESSAGE, dupe))
            }
            _ => None,
        })
        .collect::<Vec<String>>()
        .first()
        .cloned()
}

#[cfg(test)]
mod tests {
    use crate::linter::findings::L004_MESSAGE;
    use crate::read::deserialize_rules_db;
    use std::error::Error;

    #[test]
    fn lint_duplicates() -> Result<(), Box<dyn Error>> {
        let db = deserialize_rules_db(
            r#"
        [foo.bar]
        # 1
        deny perm=execute all : all
        # 2
        allow perm=open all : all
        %foo=bar
        # 3
        sdfsdf
        # 4
        allow_log perm=open all : all
        # 5
        allow perm=open all : all
        "#,
        )?;
        let r = db.rule(2).unwrap();

        assert!(r.msg.is_some());
        println!("{}", r.msg.as_ref().unwrap());
        assert!(r.msg.as_ref().unwrap().starts_with(L004_MESSAGE));
        assert!(r.msg.as_ref().unwrap().ends_with(&5.to_string()));
        Ok(())
    }
}
