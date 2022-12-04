/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::{fs, io};

use crate::check::TrustPair;
use lmdb::{Cursor, Environment, Transaction};

use crate::db::{Rec, DB};
use crate::error::Error;
use crate::error::Error::{
    LmdbFailure, LmdbNotFound, LmdbPermissionDenied, MalformattedTrustEntry, UnsupportedTrustType,
};
use crate::load::TrustSourceEntry;
use crate::source::TrustSource;
use crate::source::TrustSource::{Ancillary, System};
use crate::Trust;

pub fn parse_trust_record(s: &str) -> Result<Trust, Error> {
    let mut v: Vec<&str> = s.rsplitn(3, ' ').collect();
    v.reverse();
    match v.as_slice() {
        [f, sz, sha] => Ok(Trust {
            path: f.trim().to_string(),
            size: sz.trim().parse()?,
            hash: sha.trim().to_string(),
        }),
        _ => Err(MalformattedTrustEntry(s.to_string())),
    }
}

pub(crate) fn strtyped_trust_record(s: &str, t: &str) -> Result<(Trust, TrustSource), Error> {
    match t {
        "1" => parse_trust_record(s).map(|t| (t, System)),
        "2" => parse_trust_record(s).map(|t| (t, Ancillary)),
        v => Err(UnsupportedTrustType(v.to_string())),
    }
}

pub fn from_file(from: &Path) -> Result<Vec<TrustSourceEntry>, io::Error> {
    let r = BufReader::new(File::open(&from)?);
    let lines: Result<Vec<String>, io::Error> = r.lines().collect();
    Ok(lines?
        .iter()
        .filter(|l| !l.is_empty())
        .filter(|l| !l.trim_start().starts_with('#'))
        .map(|l| (PathBuf::from(from), l.clone()))
        .collect())
}

pub fn from_dir(from: &Path) -> Result<Vec<TrustSourceEntry>, io::Error> {
    let d_files = read_sorted_d_files(from)?;
    let mut res = vec![];
    for p in d_files {
        let mut xs = from_file(&p)?;
        res.append(&mut xs);
    }
    Ok(res)
}

/// load the fapolicyd backend lmdb database
/// parse the results into trust entries
pub fn from_lmdb(lmdb: &Path) -> Result<DB, Error> {
    let env = Environment::new().set_max_dbs(1).open(lmdb);
    let env = match env {
        Ok(e) => e,
        Err(lmdb::Error::Other(2)) => return Err(LmdbNotFound(lmdb.display().to_string())),
        Err(lmdb::Error::Other(13)) => {
            return Err(LmdbPermissionDenied(lmdb.display().to_string()))
        }
        Err(e) => return Err(LmdbFailure(e)),
    };

    let lmdb = env.open_db(Some("trust.db"))?;
    let tx = env.begin_ro_txn()?;
    let mut c = tx.open_ro_cursor(lmdb)?;
    let lookup: HashMap<String, Rec> = c
        .iter()
        .map(|i| i.map(|kv| TrustPair::new(kv).into()).unwrap())
        .collect();

    Ok(DB::from(lookup))
}

pub fn read_sorted_d_files(from: &Path) -> Result<Vec<PathBuf>, io::Error> {
    let d_files: Result<Vec<PathBuf>, io::Error> =
        fs::read_dir(from)?.map(|e| e.map(|e| e.path())).collect();

    let mut d_files: Vec<PathBuf> = d_files?
        .into_iter()
        .filter(|p| p.is_file() && p.display().to_string().ends_with(".trust"))
        .collect();

    d_files.sort_by_key(|p| p.display().to_string());

    Ok(d_files)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_record() {
        let s =
            "/home/user/my-ls 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87";
        let e = parse_trust_record(s).unwrap();
        assert_eq!(e.path, "/home/user/my-ls");
        assert_eq!(e.size, 157984);
        assert_eq!(
            e.hash,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
        );
    }

    #[test]
    fn parse_record_with_space() {
        let s =
            "/home/user/my ls 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87";
        let e = parse_trust_record(s).unwrap();
        assert_eq!(e.path, "/home/user/my ls");
        assert_eq!(e.size, 157984);
        assert_eq!(
            e.hash,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
        );
    }
}
