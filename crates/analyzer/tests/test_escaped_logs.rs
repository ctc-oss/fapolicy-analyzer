/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use fapolicy_analyzer::events::parse::parse_event;
use std::error::Error;

// todo;; test space char
const ESCAPE_CHARS: &str = "\"'`$\\!()|";

#[test]
fn test_object_escape() -> Result<(), Box<dyn Error>> {
    // not escaped
    for c in ESCAPE_CHARS.chars() {
        let c = c.to_string();
        let log = format!("rule=1 dec=deny perm=open uid=1 gid=0 pid=7 exe=xyz : path=/foo{c}bar ftype=application/x-executable");
        let (_, e) = parse_event(&log).unwrap();
        assert_eq!(e.obj.path().unwrap(), format!("/foo{c}bar"));
    }
    // escaped
    for c in ESCAPE_CHARS.chars() {
        let log = format!("rule=1 dec=deny perm=open uid=1 gid=0 pid=7 exe=xyz : path=/foo\\{c}bar ftype=application/x-executable");
        let (_, e) = parse_event(&log).unwrap();
        assert_eq!(e.obj.path().unwrap(), format!("/foo\\{c}bar"));
    }
    Ok(())
}

#[test]
fn test_subj_exe_escape() -> Result<(), Box<dyn Error>> {
    // not escaped
    for c in ESCAPE_CHARS.chars() {
        let c = c.to_string();
        let log = format!("rule=1 dec=deny perm=open uid=1 gid=0 pid=7 exe=foo{c}bar : path=/usr/bin/vi ftype=application/x-executable");
        let (_, e) = parse_event(&log).unwrap();
        assert_eq!(e.subj.exe().unwrap(), format!("foo{c}bar"));
    }
    // escaped
    for c in ESCAPE_CHARS.chars() {
        let log = format!("rule=1 dec=deny perm=open uid=1 gid=0 pid=7 exe=foo\\{c}bar : path=/usr/bin/vi ftype=application/x-executable");
        let (_, e) = parse_event(&log).unwrap();
        assert_eq!(e.subj.exe().unwrap(), format!("foo\\{c}bar"));
    }
    Ok(())
}

#[test]
fn test_subj_command_escape() -> Result<(), Box<dyn Error>> {
    // not escaped
    for c in ESCAPE_CHARS.chars() {
        let c = c.to_string();
        let log = format!("rule=1 dec=deny perm=open uid=1 gid=0 pid=7 comm=foo{c}bar : path=/usr/bin/vi ftype=application/x-executable");
        let (_, e) = parse_event(&log).unwrap();
        assert_eq!(e.subj.comm().unwrap(), format!("foo{c}bar"));
    }
    // escaped
    for c in ESCAPE_CHARS.chars() {
        let log = format!("rule=1 dec=deny perm=open uid=1 gid=0 pid=7 comm=foo\\{c}bar : path=/usr/bin/vi ftype=application/x-executable");
        let (_, e) = parse_event(&log).unwrap();
        assert_eq!(e.subj.comm().unwrap(), format!("foo\\{c}bar"));
    }
    Ok(())
}

#[test]
fn num_of_escapes() {
    assert_eq!(ESCAPE_CHARS.len(), 9)
}
