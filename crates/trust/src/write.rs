/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::db::{Rec, DB};
use std::collections::hash_map::Entry;
use std::collections::HashMap;
use std::fs::File;
use std::io::{Error, Write};
use std::path::{Path, PathBuf};
use std::{fs, io};

fn trust_dir(db: &DB, dir: &Path, compiled: &Path) -> Result<(), io::Error> {
    let mut files = HashMap::<&str, Vec<String>>::new();
    for (k, Rec { trusted: t, .. }) in db.iter() {
        let trust_string = format!("{} {} {}", t.path, t.size, t.hash);
        match files.entry(&k) {
            Entry::Vacant(e) => {
                let mut vec = e.insert(vec![trust_string]);
            }
            Entry::Occupied(mut e) => {
                e.get_mut().push(trust_string);
            }
        }
    }

    // clear existing rules.d files
    for e in fs::read_dir(dir)? {
        let f = e?.path();
        if f.display().to_string().ends_with(".trust") {
            fs::remove_file(f)?;
        }
    }

    // write trust.d files
    for (k, v) in files {
        let mut f = File::create(dir.join(k))?;
        for l in v {
            f.write_all(format!("{}\n", l).as_bytes())?;
        }
    }

    Ok(())
}

pub fn file_trust(db: &DB, to: PathBuf) -> Result<PathBuf, Error> {
    // write file trust db
    let mut tf = File::create(&to)?;
    for (path, meta) in db.iter() {
        if meta.is_ancillary() {
            tf.write_all(
                format!("{} {} {}\n", path, meta.trusted.size, meta.trusted.hash).as_bytes(),
            )?;
        }
    }
    Ok(to)
}
