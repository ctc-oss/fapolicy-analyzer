/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::db::{RuleEntry, DB};

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
        // todo;; what to do with the source text here?
        //        writing it out verbatim to the disk at deploy would be ideal
        //        but it has to be stashed somewhere until writing at deploy time
        //        Q: use compression?  stash in temp file?  stash in XDG dir?
        //        there is also the question of preserving the rule editing session
        //        as was done for trust
        match deserialize_rules_db(text) {
            Ok(r) => {
                self.db = r;
                Ok(&self.db)
            }
            Err(_) => Err("failed to deserialize db".to_string()),
        }
    }

    pub fn rule(&self, id: usize) -> Option<&RuleEntry> {
        self.db.rule(id)
    }

    pub fn apply(&self) -> &DB {
        &self.db
    }
}

#[cfg(test)]
mod tests {
    use crate::ops::Changeset;
    use std::error::Error;

    #[test]
    fn deserialize() -> Result<(), Box<dyn Error>> {
        let mut cs = Changeset::default();
        let txt = "[foo.rules]\ndeny_audit perm=open all : all";
        let _x1 = cs.set(txt);

        let txt = "[foo.rules]\nfffdeny_audit perm=open all : all";
        let _x2 = cs.set(txt)?;

        Ok(())
    }
}
