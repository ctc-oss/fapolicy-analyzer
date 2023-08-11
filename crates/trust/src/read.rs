/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::{fs, io};

use fapolicy_util::rpm::ensure_rpm_exists;
use fapolicy_util::rpm::Error::{ReadRpmDumpFailed, RpmDumpFailed};

use crate::error::Error;
use crate::source::TrustSource::{Ancillary, DFile};
use crate::source::{TrustSource, TrustSourceEntry};
use crate::{parse, Trust};

pub fn from_file(from: &Path) -> Result<Vec<TrustSourceEntry>, io::Error> {
    let r = BufReader::new(File::open(from)?);
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

pub(crate) fn file_trust(d: &Path, o: Option<&Path>) -> Result<Vec<(TrustSource, Trust)>, Error> {
    let mut d_entries: Vec<(TrustSource, String)> = match d {
        f if f.exists() => from_dir(f)?
            .into_iter()
            .map(|(o, e)| (DFile(o.display().to_string()), e))
            .collect(),
        _ => vec![],
    };

    let mut o_entries: Vec<(TrustSource, String)> = match o {
        Some(f) if f.exists() => from_file(f)?
            .iter()
            .map(|(_, e)| (Ancillary, e.clone()))
            .collect(),
        _ => vec![],
    };

    let mut entries = vec![];
    entries.append(&mut d_entries);
    entries.append(&mut o_entries);

    Ok(entries
        .iter()
        // todo;; support comments elsewhere
        .filter(|(_, txt)| !txt.is_empty() || txt.trim_start().starts_with('#'))
        .map(|(p, txt)| (p.clone(), parse::trust_record(txt.trim())))
        .filter(|(_, r)| r.is_ok())
        .map(|(p, r)| (p, r.unwrap()))
        .collect())
}

/// directly load the rpm database
/// used to analyze the fapolicyd trust db for out of sync issues
pub fn rpm_trust(rpmdb: &Path) -> Result<Vec<Trust>, Error> {
    ensure_rpm_exists()?;

    let args = vec!["-qa", "--dump", "--dbpath", rpmdb.to_str().unwrap()];
    let res = Command::new("rpm")
        .args(args)
        .output()
        .map_err(RpmDumpFailed)?;

    match String::from_utf8(res.stdout) {
        Ok(data) => Ok(parse::rpm_db_entry(&data)),
        Err(_) => Err(ReadRpmDumpFailed.into()),
    }
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
    use crate::parse;

    #[test]
    fn parse_record() {
        let s =
            "/home/user/my-ls 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87";
        let e = parse::trust_record(s).unwrap();
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
        let e = parse::trust_record(s).unwrap();
        assert_eq!(e.path, "/home/user/my ls");
        assert_eq!(e.size, 157984);
        assert_eq!(
            e.hash,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
        );
    }
}
