/*
 * Copyright Concurrent Technologies Corporation 2024
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::filter::db::DB;
use crate::filter::error::Error;
use crate::filter::load;

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
        match load::mem(text) {
            Ok(r) => {
                self.db = r;
                self.src = Some(text.to_string());
                Ok(&self.db)
            }
            Err(e) => Err(e),
        }
    }

    pub fn apply(&self) -> &DB {
        &self.db
    }
}
