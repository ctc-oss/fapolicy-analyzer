/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::rpm::Error::*;
use std::io;
use std::process::Command;
use thiserror::Error;

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
}

pub fn ensure_rpm_exists() -> Result<(), Error> {
    // we just check the version to ensure rpm is there
    Command::new("rpm")
        .arg("version")
        .output()
        .map(|_| ())
        .map_err(|_| RpmCommandNotFound)
}

pub fn rpm_q(app_name: &str) -> Result<(String, String), Error> {
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

#[cfg(test)]
mod tests {
    use super::*;

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
