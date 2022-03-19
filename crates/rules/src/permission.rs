/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fmt::{Display, Formatter};
use std::str::FromStr;

use crate::parse;
use crate::parse::StrTrace;

/// # Permission
/// Describes what kind permission is being asked for. The permission is either
///
#[derive(Clone, Debug, PartialEq)]
pub enum Permission {
    Any,
    Open,
    Execute,
}

impl Display for Permission {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.write_str("perm=")?;
        match self {
            Permission::Any => f.write_str("any"),
            Permission::Open => f.write_str("open"),
            Permission::Execute => f.write_str("execute"),
        }
    }
}

impl FromStr for Permission {
    type Err = String;

    fn from_str(i: &str) -> Result<Self, Self::Err> {
        match parse::permission(StrTrace::new(i)) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Permission from string".into()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn display() {
        assert_eq!(format!("{}", Permission::Any), "perm=any");
        assert_eq!(format!("{}", Permission::Open), "perm=open");
        assert_eq!(format!("{}", Permission::Execute), "perm=execute");
    }
}
