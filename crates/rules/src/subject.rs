/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fmt::{Display, Formatter};
use std::str::FromStr;

use crate::parse::StrTrace;
use crate::{bool_to_c, parse, SubjPart};

/// # Subject
/// The subject is the process that is performing actions on system resources.
/// The fields in the rule that describe the subject are written in a `name=value` format.
/// There can be one or more subject fields. Each field is and'ed with others to decide if a rule triggers.
#[derive(Clone, Debug, PartialEq)]
pub struct Subject {
    pub parts: Vec<Part>,
}

impl Subject {
    pub fn new(parts: Vec<Part>) -> Self {
        Subject { parts }
    }

    pub fn is_all(&self) -> bool {
        self.parts.contains(&Part::All)
    }

    pub fn all() -> Self {
        Self::new(vec![SubjPart::All])
    }

    pub fn exe(&self) -> Option<String> {
        match self.parts.iter().find(|p| matches!(p, Part::Exe(_))) {
            Some(Part::Exe(path)) => Some(path.clone()),
            _ => None,
        }
    }

    pub fn from_exe(path: &str) -> Subject {
        Subject::new(vec![SubjPart::Exe(path.into())])
    }
}

/// # Subject Field
/// Composed with logical AND to create the Subject of the rule
///
/// ## execdirs
/// The `execdirs` option will match against the following list of directories:
/// - `/usr/`
/// - `/bin/`
/// - `/sbin/`
/// - `/lib/`
/// - `/lib64/`
/// - `/usr/libexec/`
///
/// ## systemdirs
/// The `systemdirs` option will match against the same list as `execdirs` but also includes `/etc/`.
///
/// ### Currently unsupported Subject Fields
///   - `auid`: This is the login uid that the audit system assigns users when they log in to the system. Daemons have a value of -1.
///   - `sessionid`: This is the numeric session id that the audit system assigns to users when they log in. Daemons have a value of -1.
///   - `pid`: This is the numeric process id that a program has.
///   - `dir`: If you wish to match a directory, then use this by giving the full path to the directory.
///     - Its recommended to end with the `/` to ensure it matches a directory.
///     - There are 3 keywords that `dir` supports:
///       - `execdirs`
///       - `systemdirs`
///       - `untrusted`
///  - `ftype`: This option takes the mime type of a file as an argument. If you wish to check the mime type of a file while writing rules, run the following command:
///    - `file --mime-type /path-to-file`
///  - `device`: This option will match against the device that the executable resides on. To use it, start with `/dev/` and add the target device name.
///  - `pattern`: There are various ways that an attacker may try to execute code that may reveal itself in the pattern of file accesses made during program startup. This rule can take one of several options depending on which access patterns is wished to be blocked. Fapolicyd is able to detect these different access patterns and provide the access decision as soon as it identifies the pattern. The pattern type can be any of:
///    - `normal`: This matches against any ELF program that is dynamically linked.
///    - `ld_so`: This matches against access patterns that indicate that the program is being started directly by the runtime linker.
///    - `ld_preload`: This matches against access patterns that indicate that the program is being started with either `LD_PRELOAD` or `LD_AUDIT` present in the environment. Note that even without this rule, you have protection against `LD_PRELOAD` of unknown binaries when the rules are written such that trust is used to determine if a library should be opened. In that case, the preloaded library would be denied but the application will still execute. This rule makes it so that even trusted libraries can be denied and the application will not execute.
///    - `static`: This matches against ELF files that are statically linked.
///
#[derive(Clone, Debug, PartialEq)]
pub enum Part {
    /// This matches against any subject. When used, this must be the only subject in the rule.
    All,
    /// This is the shortened command name. When an interpreter starts a program, it usually renames the program to the script rather than the interpreter.
    Comm(String),
    /// This is the user id that the program is running under.
    Uid(u32),
    /// This is the group id that the program is running under.
    Gid(u32),
    /// This is the numeric process id that a program has.
    Pid(u32),
    /// This is the full path to the executable. Globbing is not supported. You may also use the special keyword \fBuntrusted\fP to match on the subject not being listed in the rpm database.
    Exe(String),
    Pattern(String),
    /// This is a boolean describing whether it is required for the subject to be in the trust database or not. A value of 1 means its required while 0 means its not. Trust checking is extended by the integrity setting in fapolicyd.conf. When trust is used on the subject, it could be a daemon. If that daemon gets updated on disk, the trustdb will be updated to the new SHA256 hash. If the integrity setting is not none, the running daemon is not likely to be trusted unless it gets restarted. The default rules are not written in a way that this would happen. But this needs to be highlighted as it may not be obvious when writing a new rule.
    Trust(bool),
}

impl From<Part> for Subject {
    fn from(p: Part) -> Self {
        Subject { parts: vec![p] }
    }
}

impl Display for Subject {
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
            Part::Comm(cmd) => f.write_fmt(format_args!("comm={}", cmd)),
            Part::Uid(id) => f.write_fmt(format_args!("uid={}", id)),
            Part::Gid(id) => f.write_fmt(format_args!("gid={}", id)),
            Part::Pid(id) => f.write_fmt(format_args!("pid={}", id)),
            Part::Exe(id) => f.write_fmt(format_args!("exe={}", id)),
            Part::Pattern(id) => f.write_fmt(format_args!("pattern={}", id)),
            Part::Trust(b) => f.write_fmt(format_args!("trust={}", bool_to_c(*b))),
        }
    }
}

impl FromStr for Subject {
    type Err = String;

    fn from_str(i: &str) -> Result<Self, Self::Err> {
        match parse::subject(StrTrace::new(i)) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Subject from string".into()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn display() {
        assert_eq!(format!("{}", Part::All), "all");
        assert_eq!(format!("{}", Part::Comm("dnf".into())), "comm=dnf");
        assert_eq!(format!("{}", Part::Uid(42)), "uid=42");
        assert_eq!(format!("{}", Part::Gid(42)), "gid=42");
        assert_eq!(format!("{}", Part::Trust(false)), "trust=0");
        assert_eq!(format!("{}", Part::Trust(true)), "trust=1");
    }

    #[test]
    fn fromstr() -> Result<(), String> {
        assert_eq!(Subject::from(Part::All), Subject::from_str("all")?);
        assert_eq!(
            Subject::from(Part::Comm("dnf".into())),
            Subject::from_str("comm=dnf")?
        );
        assert_eq!(Subject::from(Part::Uid(42)), Subject::from_str("uid=42")?);
        assert_eq!(Subject::from(Part::Gid(42)), Subject::from_str("gid=42")?);
        assert_eq!(
            Subject::from(Part::Trust(true)),
            Subject::from_str("trust=1")?
        );
        assert_eq!(
            Subject::from(Part::Trust(false)),
            Subject::from_str("trust=0")?
        );
        Ok(())
    }
}
