/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::conf::config::ConfigToken;
use std::fmt::{Display, Formatter};
use std::slice::Iter;
use Line::*;

#[derive(Clone, Debug)]
pub enum Line {
    Valid(ConfigToken),
    Invalid { k: String, v: String },
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

    pub fn is_valid(&self) -> bool {
        !self
            .lines
            .iter()
            .any(|l| matches!(l, Invalid { .. } | Malformed(_) | Duplicate(_)))
    }
}

impl From<Vec<Line>> for DB {
    fn from(lines: Vec<Line>) -> Self {
        Self { lines }
    }
}

impl Display for Line {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Valid(tok) => f.write_fmt(format_args!("{tok}")),
            Invalid { k, v } => f.write_fmt(format_args!("{k} = {v}")),
            Malformed(txt) => f.write_str(txt),
            Duplicate(tok) => f.write_fmt(format_args!("{tok}")),
            Comment(txt) => f.write_str(txt),
            BlankLine => f.write_str(""),
        }
    }
}
