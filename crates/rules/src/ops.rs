/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::db::{RuleEntry, DB};

use crate::error::Error;
use crate::error::Error::ZeroRulesDefined;
use crate::read::deserialize_rules_db;

// Mutable
#[derive(Default, Clone, Debug)]
pub struct Changeset {
    db: DB,
    src: Option<String>,
}

impl Changeset {
    pub fn get(&self) -> &DB {
        &self.db
    }

    pub fn src(&self) -> Option<&String> {
        self.src.as_ref()
    }

    pub fn set(&mut self, text: &str) -> Result<&DB, Error> {
        match deserialize_rules_db(text) {
            Ok(r) if r.is_empty_rules() => Err(ZeroRulesDefined),
            Ok(r) => {
                self.db = r;
                self.src = Some(text.to_string());
                Ok(&self.db)
            }
            Err(e) => Err(e),
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
