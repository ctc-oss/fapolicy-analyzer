/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::error::Error;
use crate::error::Error::MetaError;
use crate::events::event::Event;
use audit::Parser;
use chrono::{DateTime, NaiveDateTime, Utc};
use fapolicy_auparse::audit;
use fapolicy_auparse::logs::Logs;
use fapolicy_auparse::record::Type;
use fapolicy_auparse::record::Type::Fanotify;
use fapolicy_rules::{Decision, Object, Permission, Subject};
use std::path::PathBuf;

pub fn events(path: Option<String>) -> Result<Vec<Event>, Error> {
    let logs = match path {
        Some(p) => Logs::filtered_from(&PathBuf::from(p), Box::new(Parse), fanotify_only),
        None => Logs::filtered(Box::new(Parse), fanotify_only),
    };
    Ok(logs?.collect())
}

fn fanotify_only(x: Type) -> bool {
    x == Fanotify
}

// todo;; could add parse metrics here
pub struct Parse;
impl Parser<Event> for Parse {
    type Error = Error;

    fn parse(&self, e: audit::Event) -> Result<Event, Self::Error> {
        Ok(Event {
            rule_id: e.int("fan_info")?,
            dec: dec_from_i32(e.int("resp")?)?,
            uid: e.int("uid")?,
            gid: vec![e.int("gid")?],
            pid: e.int("pid")?,
            subj: Subject::from_exe(&e.str("exe").map(strip_escaped_quotes)?),
            perm: perm_from_i32(e.int("syscall")?)?,
            obj: Object::from_path(&e.str("name").map(strip_escaped_quotes)?),
            when: Some(DateTime::from_utc(
                NaiveDateTime::from_timestamp(e.ts(), 0),
                Utc,
            )),
        })
    }
}

// string values returned from fanotify have been observed to contain escaped quotes
fn strip_escaped_quotes(s: String) -> String {
    const PATTERN: char = '\"';
    let s = s.strip_prefix(PATTERN).unwrap_or(&s);
    s.strip_suffix(PATTERN).unwrap_or(s).to_string()
}

const EXECVE: i32 = 59;
const OPENAT: i32 = 257;

// parses the permission from the syscall id
fn perm_from_i32(value: i32) -> Result<Permission, Error> {
    match value {
        EXECVE => Ok(Permission::Execute),
        OPENAT => Ok(Permission::Open),
        _ => Err(MetaError("unsupported permission".to_string())),
    }
}

// parses the decision from the fanotify decision value
fn dec_from_i32(value: i32) -> Result<Decision, Error> {
    match value {
        0 => Err(MetaError("unknown decision 0".to_string())),
        1 => Ok(Decision::Allow),
        2 => Ok(Decision::Deny),
        _ => Err(MetaError("unsupported decision".to_string())),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use fapolicy_rules::Decision::{Allow, Deny};
    use fapolicy_rules::Permission::{Execute, Open};

    #[test]
    fn test_parse() {}

    #[test]
    fn test_perm() -> Result<(), Error> {
        assert!(perm_from_i32(0).is_err());
        assert_eq!(perm_from_i32(EXECVE)?, Execute);
        assert_eq!(perm_from_i32(OPENAT)?, Open);

        Ok(())
    }

    #[test]
    fn test_dec() -> Result<(), Error> {
        assert!(dec_from_i32(0).is_err());
        assert!(dec_from_i32(3).is_err());
        assert_eq!(dec_from_i32(1)?, Allow);
        assert_eq!(dec_from_i32(2)?, Deny);

        Ok(())
    }

    #[test]
    fn test_strip() {
        assert_eq!(strip_escaped_quotes("".into()), "");
        assert_eq!(strip_escaped_quotes("123".into()), "123");
        assert_eq!(strip_escaped_quotes("\"123".into()), "123");
        assert_eq!(strip_escaped_quotes("123\"".into()), "123");
        assert_eq!(strip_escaped_quotes("\"123\"".into()), "123");
        assert_eq!(strip_escaped_quotes("\"1\"2\"3\"".into()), "1\"2\"3");
    }
}
