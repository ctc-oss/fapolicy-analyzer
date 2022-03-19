/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fmt::{Display, Formatter};
use std::str::FromStr;

use crate::{bool_to_c, parse, ObjPart, Rvalue};

/// # Object
/// The object is the file that the subject is interacting with.
/// The fields in the rule that describe the object are written in a `name=value` format.
/// There can be one or more object fields. Each field is and'ed with others to decide if a rule triggers.
#[derive(Clone, Debug, PartialEq)]
pub struct Object {
    pub parts: Vec<Part>,
}

impl Object {
    pub fn new(parts: Vec<Part>) -> Self {
        Object { parts }
    }

    pub fn all() -> Self {
        Self::new(vec![ObjPart::All])
    }

    pub fn path(&self) -> Option<String> {
        match self.parts.iter().find(|p| matches!(p, Part::Path(_))) {
            Some(Part::Path(path)) => Some(path.clone()),
            _ => None,
        }
    }

    pub fn from_path(path: &str) -> Object {
        Object::new(vec![ObjPart::Path(path.into())])
    }
}

/// # Object Field
/// Composed with logical AND to create the Object of the rule
///
/// ### Currently unsupported Object Fields
///   - `sha256hash`: This option matches against the sha256 hash of the file being accessed.
///     - The hash in the rules should be all lowercase letters and do NOT start with 0x.
///     - Lowercase is the default output of sha256sum.
///
#[derive(Clone, Debug, PartialEq)]
pub enum Part {
    /// This matches against any subject. When used, this must be the only subject in the rule.
    All,
    /// This option will match against the device that the file being accessed resides on. To use it, start with `/dev/` and add the target device name.
    Device(String),
    /// If you wish to match on access to any file in a directory, then use this by giving the full path to the directory.
    ///  - Its recommended to end with the `/` to ensure it matches a directory.
    ///  - There are 3 keywords that `dir` supports:
    ///    - `execdirs`
    ///    - `systemdirs`
    ///    - `untrusted`
    ///
    /// ### See the `dir` option under Subject for an explanation of these keywords.
    Dir(String),
    /// This option matches against the mime type of the file being accessed. See `ftype` under Subject for more information on determining the mime type.
    FileType(Rvalue),
    /// This is the full path to the file that will be accessed. Globbing is not supported. You may also use the special keyword `untrusted` to match on the subject not being listed in the rpm database.
    Path(String),
    /// This is a boolean describing whether it is required for the object to be in the trust database or not. A value of 1 means its required while 0 means its not. Trust checking is extended by the integrity setting in fapolicyd.conf.
    Trust(bool),
}

impl From<Part> for Object {
    fn from(p: Part) -> Self {
        Object { parts: vec![p] }
    }
}

impl Display for Object {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let s: String = self
            .parts
            .iter()
            .map(|p| format!("{}", p))
            .collect::<Vec<String>>()
            .join(" ");
        f.write_fmt(format_args!("{}", s))
    }
}

impl Display for Part {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Part::All => f.write_str("all"),
            Part::Device(p) => f.write_fmt(format_args!("device={}", p)),
            Part::Dir(p) => f.write_fmt(format_args!("dir={}", p)),
            Part::FileType(t) => f.write_fmt(format_args!("ftype={}", t)),
            Part::Path(p) => f.write_fmt(format_args!("path={}", p)),
            Part::Trust(b) => f.write_fmt(format_args!("trust={}", bool_to_c(*b))),
        }
    }
}

#[cfg(test)]
mod tests {
    use crate::file_type::Rvalue::Literal;

    use super::*;

    #[test]
    fn display() {
        assert_eq!(format!("{}", Part::All), "all");
        assert_eq!(format!("{}", Part::Dir("/foo".into())), "dir=/foo");
        assert_eq!(
            format!("{}", Part::Device("/dev/cdrom".into())),
            "device=/dev/cdrom"
        );
        assert_eq!(
            format!(
                "{}",
                Part::FileType(Literal("application/x-sharedlib".into()))
            ),
            "ftype=application/x-sharedlib"
        );
    }

    #[test]
    fn display_trusted() {
        assert_eq!(
            format!("{}", Object::new(vec![Part::All, Part::Trust(true)])),
            "all trust=1"
        );
        assert_eq!(
            format!(
                "{}",
                Object::new(vec![Part::Dir("/foo".into()), Part::Trust(true)])
            ),
            "dir=/foo trust=1"
        );
        assert_eq!(
            format!(
                "{}",
                Object::new(vec![Part::Device("/dev/cdrom".into()), Part::Trust(true)])
            ),
            "device=/dev/cdrom trust=1"
        );
        assert_eq!(
            format!(
                "{}",
                Object::new(vec![
                    Part::FileType(Literal("application/x-sharedlib".into())),
                    Part::Trust(true)
                ])
            ),
            "ftype=application/x-sharedlib trust=1"
        );
    }
}
