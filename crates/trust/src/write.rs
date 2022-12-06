/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::db::{Rec, DB};
use crate::source::TrustSource;
use std::collections::hash_map::Entry;
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;
use std::path::Path;
use std::{fs, io};

pub fn db(db: &DB, trust_d: &Path, trust_file: Option<&Path>) -> Result<(), io::Error> {
    dir(db, trust_d)?;
    if let Some(trust_f) = trust_file {
        file(db, trust_f)?;
    }
    Ok(())
}

fn dir(db: &DB, dir: &Path) -> Result<(), io::Error> {
    let mut files = HashMap::<&str, Vec<String>>::new();
    for (
        _,
        Rec {
            trusted: t,
            source: o,
            ..
        },
    ) in db.iter()
    {
        if let Some(TrustSource::DFile(o)) = o {
            let trust_string = format!("{} {} {}", t.path, t.size, t.hash);
            match files.entry(o) {
                Entry::Vacant(e) => {
                    e.insert(vec![trust_string]);
                }
                Entry::Occupied(mut e) => {
                    e.get_mut().push(trust_string);
                }
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

fn file(db: &DB, to: &Path) -> Result<(), io::Error> {
    // write file trust db
    let mut tf = File::create(&to)?;
    for (path, rec) in db.iter() {
        match rec.source {
            None | Some(TrustSource::Ancillary) => {
                tf.write_all(
                    format!("{} {} {}\n", path, rec.trusted.size, rec.trusted.hash).as_bytes(),
                )?;
            }
            _ => {}
        }
    }
    Ok(())
}
