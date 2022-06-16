/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::db::DB;
use crate::error::Error;
use crate::load::RuleSource;
use crate::parser;
use crate::read::deserialize_rules_db;
use std::collections::HashMap;
use std::io;

// Mutable
// Text backed container that deserializes on the fly
#[derive(Default, Clone, Debug)]
pub struct Changeset {
    text: String,
}

impl Changeset {
    // todo;; how to properly convey lints and errors in the parse fail?
    //        perhaps just roll it up to a _simple_ Error/Warn/Ok result enum
    pub fn set(&mut self, text: &str) -> Result<(), String> {
        deserialize_rules_db(text)
            .map(|_| ())
            .map_err(|_| "".to_string())
    }

    pub fn apply() -> Result<DB, Error> {
        todo!()
    }
}

#[cfg(test)]
mod tests {
    use crate::ops::Changeset;

    #[test]
    fn deserialize() {
        let mut cs = Changeset::default();
        let txt = "[foo.rules]\ndeny_audit perm=open all : all";
        let x1 = cs.set(txt);

        let txt = "[foo.rules]\nfffdeny_audit perm=open all : all";
        let x2 = cs.set(txt);

        println!("...");
    }
}
