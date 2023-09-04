/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::conf::config::ConfigToken;
use std::slice::Iter;

#[derive(Clone, Debug)]
pub enum Line {
    Valid(ConfigToken),
    Invalid(String, String),
    Malformed(String),
    Duplicate(ConfigToken),
    Comment(String),
    BlankLine,
}

#[derive(Clone, Debug, Default)]
pub struct DB {
    lines: Vec<Line>,
}

impl DB {
    pub fn is_empty(&self) -> bool {
        self.lines.is_empty()
    }

    pub fn iter(&self) -> Iter<'_, Line> {
        self.lines.iter()
    }
}

impl From<Vec<Line>> for DB {
    fn from(lines: Vec<Line>) -> Self {
        Self { lines }
    }
}
