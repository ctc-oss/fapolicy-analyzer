/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::conf::db::DB;
use crate::conf::error::Error;
use crate::conf::read;

pub fn file(path: &str) -> Result<DB, Error> {
    read::file(path.into())
}

pub fn mem(txt: &str) -> Result<DB, Error> {
    read::mem(txt)
}

pub fn with_error_message(txt: &str) -> Result<DB, String> {
    mem(txt).map_err(|e| e.to_string())
}

#[cfg(test)]
mod test {
    use super::*;
    use crate::conf::config::Entry;
    use crate::Config;
    use assert_matches::assert_matches;

    #[test]
    fn parse_good_txt_config() {
        let db = &mem("permissive=0\nuid=fapolicyd").expect("parse");
        let x: Config = db.into();
        assert_matches!(x.permissive, Entry::Valid(false));
        assert_matches!(x.uid, Entry::Valid(uid) if uid == "fapolicyd");
        assert_matches!(x.gid, Entry::Missing);
    }

    #[test]
    fn parse_bad_txt_config() -> Result<(), Box<dyn std::error::Error>> {
        let db = &mem("permissive=true")?;
        let x: Config = db.into();
        assert_matches!(x.permissive, Entry::Invalid(p) if p == "true");
        assert_matches!(x.gid, Entry::Missing);

        Ok(())
    }
}
