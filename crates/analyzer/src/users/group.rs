/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fmt::{Display, Formatter};
use std::str::FromStr;

use serde::Deserialize;
use serde::Serialize;

use crate::users::parse;

/// # Group
/// Represents a /etc/group Group
///
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Group {
    pub name: String,
    pub gid: u32,
    pub users: Vec<String>,
}

impl Display for Group {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.write_fmt(format_args!(
            "{}:x:{}:{}",
            self.name,
            self.gid,
            self.users.join(",")
        ))
    }
}

impl FromStr for Group {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match parse::group(s) {
            Ok((_, u)) => Ok(u),
            Err(_) => Err("Failed to parse User from string".into()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn testgroup0() -> Group {
        Group {
            name: "root".into(),
            gid: 0,
            users: vec![],
        }
    }

    fn testgroup1() -> Group {
        Group {
            name: "tty".into(),
            gid: 5,
            users: vec!["syslog".into()],
        }
    }

    #[test]
    fn display() {
        assert_eq!(format!("{}", testgroup0()), "root:x:0:");
        assert_eq!(format!("{}", testgroup1()), "tty:x:5:syslog");
    }

    #[test]
    fn fromstr() {
        assert_eq!(testgroup0(), Group::from_str("root:x:0:").unwrap());
    }
}
