/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

// todo;; tracking the fapolicyd specific bits in here to determine if bindings are worthwhile

use std::thread::sleep;
use std::time::Duration;

use crate::error::Error;
use crate::error::Error::FapolicydReloadFail;
use crate::svc::Handle;

pub const TRUST_DB_PATH: &str = "/var/lib/fapolicyd";
pub const TRUST_DB_NAME: &str = "trust.db";
pub const TRUST_FILE_PATH: &str = "/etc/fapolicyd/fapolicyd.trust";
pub const RULES_FILE_PATH: &str = "/etc/fapolicyd/rules.d";
pub const RPM_DB_PATH: &str = "/var/lib/rpm";
pub const FIFO_PIPE: &str = "/run/fapolicyd/fapolicyd.fifo";

const USR_SHARE_ALLOWED_EXTS: [&str; 15] = [
    "pyc", "pyo", "py", "rb", "pl", "stp", "js", "jar", "m4", "php", "el", "pm", "lua", "class",
    "elc",
];

#[derive(Clone, Debug)]
pub enum Version {
    Unknown,
    Release { major: u8, minor: u8, patch: u8 },
}

const RETRIES: u8 = 15;
pub fn reload() -> Result<(), Error> {
    let fapolicyd = Handle::default();
    fapolicyd.stop()?;
    for _ in 0..RETRIES {
        sleep(Duration::from_secs(1));
        if !fapolicyd.active()? {
            fapolicyd.start()?;
            break;
        }
    }
    for _ in 0..RETRIES {
        sleep(Duration::from_secs(1));
        if fapolicyd.active()? {
            return Ok(());
        }
    }
    Err(FapolicydReloadFail(
        "Could not reload after 10 tries".to_string(),
    ))
}

/// filtering logic as implemented by fapolicyd rpm backend
pub(crate) fn keep_entry(p: &str) -> bool {
    match p {
        s if s.starts_with("/usr/share") => {
            USR_SHARE_ALLOWED_EXTS.iter().any(|ext| s.ends_with(*ext)) || s.contains("/libexec/")
        }
        s if s.starts_with("/usr/src") => s.contains("/scripts/") || s.contains("/tools/objtool/"),
        s if s.starts_with("/usr/include") => false,
        _ => true,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

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
