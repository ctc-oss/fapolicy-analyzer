/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::io;
use std::process::Command;

use nom::bytes::complete::tag;
use nom::character::complete::alphanumeric1;
use nom::character::complete::digit1;
use nom::character::complete::line_ending;
use nom::character::complete::space1;
use nom::combinator::{iterator, opt};
use nom::sequence::{delimited, preceded, terminated};
use nom::{IResult, InputIter, Parser};
use thiserror::Error;

use crate::fapolicyd;
use fapolicy_api::trust::Trust;

use crate::fapolicyd::keep_entry;
use crate::rpm::Error::{
    MalformedVersionString, ReadRpmDumpFailed, RpmCommandNotFound, RpmDumpFailed, RpmEntryNotFound,
    RpmEntryVersionParseFailed,
};

#[derive(Error, Debug)]
pub enum Error {
    #[error("rpm: command not found")]
    RpmCommandNotFound,
    #[error("rpm dump failed: {0}")]
    RpmDumpFailed(io::Error),
    #[error("read rpm dump failed")]
    ReadRpmDumpFailed,
    #[error("application not found")]
    RpmEntryNotFound,
    #[error("could not parse {0}")]
    RpmEntryVersionParseFailed(String),
    #[error("could not parse version string {0}")]
    MalformedVersionString(String),
}

#[derive(Debug)]
struct RpmDbEntry {
    pub path: String,
    pub size: u64,
    pub hash: Option<String>,
}

pub fn ensure_rpm_exists() -> Result<(), Error> {
    // we just check the version to ensure rpm is there
    Command::new("rpm")
        .arg("version")
        .output()
        .map(|_| ())
        .map_err(|_| RpmCommandNotFound)
}

pub fn fapolicyd_version() -> fapolicyd::Version {
    match rpm_q_fapolicyd() {
        Ok(v) => v,
        Err(e) => {
            eprintln!("Unable to detect fapolicyd version: {:?}", e);
            fapolicyd::Version::Unknown
        }
    }
}

fn rpm_q_fapolicyd() -> Result<fapolicyd::Version, Error> {
    let (_, v) = rpm_q("fapolicyd")?;
    match parse_semver(&v) {
        Ok((_, (major, minor, patch))) => Ok(fapolicyd::Version::Release {
            major,
            minor,
            patch,
        }),
        Err(_) => Err(MalformedVersionString(v)),
    }
}

fn rpm_q(app_name: &str) -> Result<(String, String), Error> {
    ensure_rpm_exists()?;

    let args = vec!["-q", app_name];
    let res = Command::new("rpm")
        .args(args)
        .output()
        .map_err(|_| RpmEntryNotFound)?;

    match String::from_utf8(res.stdout) {
        Ok(data) => {
            let (lhs, rhs) = parse_rpm_q(data.trim())?;
            Ok((lhs, rhs))
        }
        Err(_) => Err(ReadRpmDumpFailed),
    }
}

fn parse_rpm_q(s: &str) -> Result<(String, String), Error> {
    if let Some((s, _)) = s.rsplit_once('-') {
        if let Some((lhs, rhs)) = s.split_once('-') {
            return Ok((lhs.to_string(), rhs.to_string()));
        }
    }
    Err(RpmEntryVersionParseFailed(s.trim().to_string()))
}

// fapolicyd has been observed to have two and three part version numbers
// the parser is constructed to allow the third part to be optional, defaulting to 0
fn parse_semver(i: &str) -> IResult<&str, (u8, u8, u8)> {
    nom::combinator::complete(nom::sequence::tuple((
        terminated(digit1, tag(".")),
        digit1,
        opt(preceded(tag("."), digit1)),
    )))(i)
    .map(|(r, (major, minor, patch))| {
        (
            r,
            (
                major.parse::<u8>().unwrap(),
                minor.parse::<u8>().unwrap(),
                patch.unwrap_or("0").parse::<u8>().unwrap(),
            ),
        )
    })
}

/// directly load the rpm database
/// used to analyze the fapolicyd trust db for out of sync issues
pub fn load_system_trust(rpmdb: &str) -> Result<Vec<Trust>, Error> {
    ensure_rpm_exists()?;

    let args = vec!["-qa", "--dump", "--dbpath", rpmdb];
    let res = Command::new("rpm")
        .args(args)
        .output()
        .map_err(RpmDumpFailed)?;

    match String::from_utf8(res.stdout) {
        Ok(data) => Ok(parse(&data)),
        Err(_) => Err(ReadRpmDumpFailed),
    }
}

fn contains_no_files(s: &str) -> nom::IResult<&str, Option<RpmDbEntry>> {
    delimited(tag("("), tag("contains no files"), tag(")"))(s).map(|x| (x.0, None))
}

fn parse(s: &str) -> Vec<Trust> {
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

//////////

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn with_contains_no_files_lines() {
        let full = format!(
            "{}\n,{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n",
            NF, A, NF, B, NF, C, NF, D, NF
        );
        let r = parse(&full);
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
        let files: Vec<Trust> = parse(&abc);
        assert_eq!(files.len(), 2);
    }

    #[test]
    fn test_parse_semver() -> Result<(), Box<dyn std::error::Error>> {
        // 2
        let v = "1.1";
        assert_eq!((1, 1, 0), parse_semver(v)?.1);

        let v = "0.0";
        assert_eq!((0, 0, 0), parse_semver(v)?.1);

        let v = "0.99";
        assert_eq!((0, 99, 0), parse_semver(v)?.1);

        // 3
        let v = "1.0.3";
        assert_eq!((1, 0, 3), parse_semver(v)?.1);

        let v = "11.0.3";
        assert_eq!((11, 0, 3), parse_semver(v)?.1);

        let v = "0.9.3";
        assert_eq!((0, 9, 3), parse_semver(v)?.1);

        Ok(())
    }

    #[test]
    // test parse of 2 and 3 part version strings for both fc and el
    fn test_parse_rpm_q() -> Result<(), Box<dyn std::error::Error>> {
        assert_eq!(
            ("fapolicyd".to_string(), "1.1".to_string()),
            parse_rpm_q("fapolicyd-1.1-6.el8.x86_64")?
        );
        assert_eq!(
            ("fapolicyd".to_string(), "1.1.1".to_string()),
            parse_rpm_q("fapolicyd-1.1.1-6.el8.x86_64")?
        );

        assert_eq!(
            ("fapolicyd".to_string(), "1.0.3".to_string()),
            parse_rpm_q("fapolicyd-1.0.3-2.fc34.x86_64")?
        );
        assert_eq!(
            ("fapolicyd".to_string(), "1.0".to_string()),
            parse_rpm_q("fapolicyd-1.0-2.fc34.x86_64")?
        );

        Ok(())
    }
}
