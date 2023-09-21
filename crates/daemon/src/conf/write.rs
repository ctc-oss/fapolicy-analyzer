/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::conf::DB;
use std::fs::File;
use std::io;
use std::io::Write;
use std::path::Path;

pub fn db(db: &DB, to: &Path) -> Result<(), io::Error> {
    let mut conf_file = File::create(to)?;
    for line in db.iter() {
        conf_file.write_all(format!("{}\n", line).as_bytes())?;
    }
    Ok(())
}
