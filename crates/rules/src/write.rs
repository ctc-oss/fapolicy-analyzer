/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::db::DB;
use crate::write;
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;
use std::path::Path;
use std::{fs, io};

pub fn db(db: &DB, to: &Path) -> Result<(), io::Error> {
    if to.is_dir() {
        let parent = to.parent().expect("Cannot write to /");
        rules_dir(db, to, &parent.join("compiled.rules"))
    } else {
        rules_file(db, to)
    }
}

fn rules_dir(db: &DB, dir: &Path, compiled: &Path) -> Result<(), io::Error> {
    let mut files = HashMap::<&str, Vec<String>>::new();
    for (_, (k, v)) in db.iter() {
        if !files.contains_key(k.as_str()) {
            files.insert(k, vec![]);
        }
        files.get_mut(k.as_str()).unwrap().push(v.to_string());
    }

    // clear existing rules.d files
    for e in fs::read_dir(dir)? {
        let f = e?.path();
        if f.display().to_string().ends_with(".rules") {
            fs::remove_file(f)?;
        }
    }

    // write rules.d files
    for (k, v) in files {
        let mut rf = File::create(dir.join(k))?;
        for l in v {
            rf.write_all(format!("{}\n", l).as_bytes())?;
        }
    }

    // write compiled.rules
    // todo;; get this from config or constants
    compiled_rules(&db, compiled)?;

    Ok(())
}

pub fn compiled_rules(db: &DB, path: &Path) -> Result<(), io::Error> {
    // write compiled.rules
    // todo;; get this from config or constants
    let mut rf = File::create(path)?;
    for (_, (_, e)) in db.iter() {
        rf.write_all(format!("{}\n", e).as_bytes())?;
    }

    Ok(())
}

fn rules_file(db: &DB, to: &Path) -> Result<(), io::Error> {
    let mut rf = File::create(to)?;
    for (_, (_, e)) in db.iter() {
        rf.write_all(format!("{}\n", e).as_bytes())?;
    }
    Ok(())
}
