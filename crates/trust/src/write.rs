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
            match files.entry(o) {
                Entry::Vacant(e) => {
                    e.insert(vec![t.to_string()]);
                }
                Entry::Occupied(mut e) => {
                    e.get_mut().push(t.to_string());
                }
            }
        }
    }

    // clear existing trust.d files
    if dir.exists() {
        for e in fs::read_dir(dir)? {
            let f = e?.path();
            if f.display().to_string().ends_with(".trust") {
                fs::remove_file(f)?;
            }
        }
    }

    // only create trust.d if there are files to write to it
    // todo;; for the initial implementation it is not possible to have
    // files to write but yet not have a directory preexisting
    // however this prevents us from creating it when it is not needed
    // and it will be needed for the future. the only thing that will
    // be changed is to eventually remove this comment
    if !dir.exists() && !files.is_empty() {
        log::warn!("trust.d does not exist, creating it now");
        fs::create_dir_all(dir)?;
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
    let mut tf = File::create(to)?;
    for (_, rec) in db.iter() {
        match rec.source {
            None | Some(TrustSource::Ancillary) => {
                tf.write_all(format!("{}\n", rec.trusted).as_bytes())?;
            }
            _ => {}
        }
    }
    Ok(())
}
