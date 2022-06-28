/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::db::{RuleDef, DB};

use crate::read::deserialize_rules_db;

// Mutable
#[derive(Default, Clone, Debug)]
pub struct Changeset {
    db: DB,
}

impl Changeset {
    pub fn get(&self) -> &DB {
        &self.db
    }

    // todo;; how to properly convey lints and errors in the parse fail?
    //        perhaps just roll it up to a _simple_ Error/Warn/Ok result enum
    pub fn set(&mut self, text: &str) -> Result<&DB, String> {
        match deserialize_rules_db(text) {
            Ok(r) => {
                self.db = r;
                Ok(&self.db)
            }
            Err(_) => Err("failed to deserialize db".to_string()),
        }
    }

    pub fn rule(&self, id: usize) -> Option<&RuleDef> {
        self.db.get(id)
    }

    pub fn apply(&self) -> DB {
        DB::default()
    }
}

#[cfg(test)]
mod tests {
    use crate::ops::Changeset;
    use std::error::Error;

    #[test]
    fn deserialize_absolute() -> Result<(), Box<dyn Error>> {
        let mut cs = Changeset::default();
        let txt = "[/foo.rules]\ndeny_audit perm=open all : all";
        let _x1 = cs.set(txt);

        let txt = "[/foo.rules]\nfffdeny_audit perm=open all : all";
        let _x2 = cs.set(txt)?;

        Ok(())
    }
}
