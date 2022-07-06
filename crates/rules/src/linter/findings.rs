/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::db::DB;
use crate::Rule;
use std::path::PathBuf;

pub(crate) const L001_MESSAGE: &str = "Using any+all+all here will short-circuit all other rules.";
pub fn l001(id: usize, r: &Rule, db: &DB) -> Option<String> {
    if id < db.len() // rules are indexed from 1
        && r.perm.is_any()
        && r.subj.is_all()
        && r.obj.is_all()
    {
        Some(L001_MESSAGE.to_string())
    } else {
        None
    }
}

pub fn l002(_id: usize, r: &Rule, _db: &DB) -> Option<String> {
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

pub fn l003(_id: usize, r: &Rule, _db: &DB) -> Option<String> {
    if let Some(path) = r.obj.path().map(PathBuf::from) {
        if !path.exists() {
            Some("The path specified does not exist.".to_string())
        } else {
            None
        }
    } else {
        None
    }
}
