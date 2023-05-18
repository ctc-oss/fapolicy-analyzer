/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fmt::{Display, Formatter};

#[derive(Clone, Debug, Eq, PartialEq, Hash)]
pub enum DirType {
    /// Match a directory using the full path to the directory. Its recommended to end with the /
    /// to ensure it matches a directory.
    Path(String),
    /// The execdirs option will match against the following list of directories:
    /// /usr/, /bin/, /sbin/, /lib/, /lib64/, /usr/libexec/
    ExecDirs,
    /// The systemdirs option will match against the same list as execdirs but also includes /etc/.
    SystemDirs,
    /// The  untrusted option will look up the current executable's full path in the rpm database to see
    /// if the executable is known to the system. The rule will trigger if the file in question  is  not
    /// in  the  trust database. This option is deprecated in favor of using obj_trust with execute per‐
    /// mission when writing rules.
    Untrusted,
}

impl Display for DirType {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            DirType::Path(v) => f.write_str(v),
            DirType::ExecDirs => f.write_str("execdirs"),
            DirType::SystemDirs => f.write_str("systemdirs"),
            DirType::Untrusted => f.write_str("untrusted"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn display() {
        assert_eq!(format!("{}", DirType::Path("/foo/".to_string())), "/foo/");
        assert_eq!(format!("{}", DirType::ExecDirs), "execdirs");
        assert_eq!(format!("{}", DirType::SystemDirs), "systemdirs");
        assert_eq!(format!("{}", DirType::Untrusted), "untrusted");
    }
}
