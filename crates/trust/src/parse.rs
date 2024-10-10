/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::error::Error;
use crate::error::Error::{MalformattedTrustEntry, UnsupportedTrustType};
use crate::load::keep_entry;
use crate::source::TrustSource;
use crate::source::TrustSource::{Ancillary, System};
use crate::Trust;
use nom::bytes::complete::tag;
use nom::character::complete::{alphanumeric1, digit1, line_ending, space1};
use nom::combinator::iterator;
use nom::sequence::{delimited, terminated};
use nom::{InputIter, Parser};

/// Parse a trust record from a string
/// Formatted as three space separated values
/// PATH SIZE HASH
/// The hash value may contain additional leading whitespace, for sha1 for example
pub fn trust_record(s: &str) -> Result<Trust, Error> {
    if let Some((i, hash)) = s.trim().rsplit_once(' ') {
        if let Some((f, sz)) = i.trim().rsplit_once(' ') {
            let size = sz
                .parse()
                .map_err(|e| MalformattedTrustEntry(format!("size parse {e} [{s}]")))?;
            Ok(Trust {
                path: f.to_owned(),
                size,
                hash: hash.to_owned(),
            })
        } else {
            Err(MalformattedTrustEntry(format!("path parse [{s}]")))
        }
    } else {
        Err(MalformattedTrustEntry(format!("hash parse [{s}]")))
    }
}

/// Parse a trust record with type metadata data
/// Formatted as four space separated values
/// TYPE PATH SIZE HASH
/// The TYPE can be system or ancillary
/// 0 - unknown
/// 1 - RPM
/// 2 - File
/// 3 - Debian
pub(crate) fn strtyped_trust_record(s: &str, t: &str) -> Result<(Trust, TrustSource), Error> {
    match t {
        "1" => trust_record(s).map(|t| (t, System)),
        "2" => trust_record(s).map(|t| (t, Ancillary)),
        v => Err(UnsupportedTrustType(v.to_string())),
    }
}

#[derive(Debug)]
struct RpmDbEntry {
    pub path: String,
    pub size: u64,
    pub hash: Option<String>,
}

pub(crate) fn rpm_db_entry(s: &str) -> Vec<Trust> {
    iterator(s, terminated(contains_no_files.or(parse_line), line_ending))
        .collect::<Vec<Option<RpmDbEntry>>>()
        .iter()
        .flatten()
        .filter(|e| keep_entry(&e.path))
        .flat_map(|e| {
            e.hash.as_ref().map(|hash| Trust {
                path: e.path.clone(),
                size: e.size,
                hash: hash.clone(),
            })
        })
        .collect()
}

fn contains_no_files(s: &str) -> nom::IResult<&str, Option<RpmDbEntry>> {
    delimited(tag("("), tag("contains no files"), tag(")"))(s).map(|x| (x.0, None))
}

fn filepath(i: &str) -> nom::IResult<&str, &str> {
    nom::bytes::complete::is_not(" \t\n")(i)
}

fn modestring(i: &str) -> nom::IResult<&str, &str> {
    nom::bytes::complete::is_a("01234567")(i)
}

fn digest_or_not(i: &str) -> Option<&str> {
    if i.iter_elements().all(|c| c == '0') {
        None
    } else {
        Some(i)
    }
}

fn int_to_bool(i: &str) -> bool {
    match i {
        "0" => false,
        "1" => true,
        v => panic!("invalid bool value {}", v),
    }
}

fn is_dir(mode: &str) -> bool {
    mode.starts_with("040")
}

/// path size mtime digest mode owner group isconfig isdoc rdev symlink
fn parse_line(i: &str) -> nom::IResult<&str, Option<RpmDbEntry>> {
    match nom::combinator::complete(nom::sequence::tuple((
        terminated(filepath, space1),
        terminated(digit1, space1),
        terminated(digit1, space1),
        terminated(alphanumeric1, space1),
        terminated(modestring, space1),
        terminated(alphanumeric1, space1),
        terminated(alphanumeric1, space1),
        terminated(digit1, space1).map(int_to_bool),
        terminated(digit1, space1).map(int_to_bool),
        terminated(digit1, space1),
        filepath,
    )))(i)
    {
        Ok((
            remaining_input,
            (
                path,
                size,
                _, // mtime
                digest,
                mode,
                _, // owner
                _, // group
                is_cfg,
                is_doc,
                _, // rdev
                _, // symlink
            ),
        )) if !is_cfg && !is_doc && !is_dir(mode) => Ok((
            remaining_input,
            Some(RpmDbEntry {
                path: path.to_string(),
                size: size.parse().unwrap(),
                hash: digest_or_not(digest).map(|s| s.to_string()),
            }),
        )),
        Ok((remaining_input, _)) => Ok((remaining_input, None)),
        Err(e) => Err(e),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn with_contains_no_files_lines() {
        let full = format!(
            "{}\n,{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n",
            NF, A, NF, B, NF, C, NF, D, NF
        );
        let r = rpm_db_entry(&full);
        assert_eq!(2, r.len());
    }

    static NF: &str = "(contains no files)";
    static A: &str = "/usr/bin/hostname 21664 1557584275 26532eeae676157e70231d911474e48d31085b5f2e511ce908349dbb02f0f69c 0100755 root root 0 0 0 X";
    static B: &str = "/usr/share/man/man1/dnsdomainname.1.gz 13 1557584275 0000000000000000000000000000000000000000000000000000000000000000 0120777 root root 0 1 0 hostname.1.gz";
    static C: &str = "/usr/lib/.build-id/a8/a7ee9d5002492edfc62e3e2e44149e981f9866 28 1557584275 0000000000000000000000000000000000000000000000000000000000000000 0120777 root root 0 0 0 ../../../../usr/bin/hostname";
    static D: &str = "/usr/bin/tar 459928 1595282074 7642954ec2d8cd43ac345eca0b4a20fc5d44811a309e62fa78340cce8cff10cc 0100755 root root 0 0 0 X";

    #[test]
    fn parse_a() {
        let expected = RpmDbEntry {
            path: "/usr/bin/hostname".to_string(),
            size: 21664,
            hash: Some(
                "26532eeae676157e70231d911474e48d31085b5f2e511ce908349dbb02f0f69c".to_string(),
            ),
        };
        let (_, actual) = parse_line(A).unwrap();

        let e = actual.as_ref().unwrap();
        assert_eq!(e.path, expected.path);
        assert_eq!(e.size, expected.size);
        assert_eq!(e.hash, expected.hash);
    }

    #[test]
    fn parse_b() {
        // b is doc, filtered out
        let (_, actual) = parse_line(B).unwrap();
        assert!(actual.is_none());
    }

    #[test]
    fn parse_c() {
        let expected = RpmDbEntry {
            path: "/usr/lib/.build-id/a8/a7ee9d5002492edfc62e3e2e44149e981f9866".to_string(),
            size: 28,
            hash: None,
        };
        let (_, actual) = parse_line(C).unwrap();

        let e = actual.as_ref().unwrap();
        assert_eq!(e.path, expected.path);
        assert_eq!(e.size, expected.size);
        assert_eq!(e.hash, expected.hash);
    }

    #[test]
    fn parse_db() {
        let abc = format!("{}\n{}\n{}\n{}\n", A, B, C, D);
        let files: Vec<Trust> = rpm_db_entry(&abc);
        assert_eq!(files.len(), 2);
    }

    fn drop_entry(path: &str) -> bool {
        !keep_entry(path)
    }

    #[test]
    fn test_drop_path() {
        // keep entries from /usr/share that are approved ext
        assert!(keep_entry("/usr/share/bar.py"));

        // drop entries from /usr/share that are not approved ext
        assert!(drop_entry("/usr/share/bar.exe"));

        // unless they are in libexec
        assert!(keep_entry("/usr/share/libexec/bar.exe"));

        // drop entries from /usr/include that are not approved ext
        assert!(drop_entry("/usr/include/bar.h"));

        // todo;; some audit results
        // assert!(drop_entry("/usr/lib64/python3.6/LICENSE.txt"));
        // assert!(drop_entry(
        //     "/usr/share/bash-completion/completions/ctrlaltdel"
        // ));
        // assert!(drop_entry("/usr/share/zoneinfo/right/America/Santa_Isabel"));

        // all others are left in place
        assert!(keep_entry("/foo/bar"));
        assert!(keep_entry("/foo/bar.py"));
    }
}
