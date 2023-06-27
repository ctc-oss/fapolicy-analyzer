use crate::error::Error;
use crate::error::Error::MetaError;
use crate::events::event::Event;
use chrono::{DateTime, NaiveDateTime, Utc};
use fapolicy_auparse::logs::Logs;
use fapolicy_auparse::record::Type;
use fapolicy_auparse::record::Type::Fanotify;
use fapolicy_auparse_sys::event::Event as AuditEvent;
use fapolicy_rules::{Decision, Object, Permission, Subject};
use std::convert::TryFrom;
use std::path::PathBuf;

pub fn events(path: Option<String>) -> Result<Vec<Event>, Error> {
    println!("loading log from {path:?}");
    let logs = match path {
        Some(p) => Logs::filtered_from(&PathBuf::from(p), parse, fanotify_only),
        None => Logs::filtered(parse, fanotify_only),
    };
    Ok(logs.expect("failed to read audit log").collect())
}

fn fanotify_only(x: Type) -> bool {
    x == Fanotify
}

fn parse(e: AuditEvent) -> Option<Event> {
    Some(Event {
        rule_id: e.int("fan_info").expect("fan_info"),
        dec: dec_from_i32(e.int("resp").expect("resp")).expect("dec"),
        uid: e.int("uid").expect("uid"),
        gid: vec![e.int("gid").expect("gid")],
        pid: e.int("pid").expect("pid"),
        subj: Subject::from_exe(
            e.str("exe")
                .expect("exe")
                .strip_prefix("\"")
                .unwrap()
                .strip_suffix("\"")
                .unwrap(),
        ),
        perm: perm_from_i32(e.int("syscall").expect("syscall")).expect("perm"),
        obj: Object::from_path(
            e.str("name")
                .expect("name")
                .strip_prefix("\"")
                .unwrap()
                .strip_suffix("\"")
                .unwrap(),
        ),
        when: Some(DateTime::from_utc(
            NaiveDateTime::from_timestamp(e.ts(), 0),
            Utc,
        )),
    })
}

fn perm_from_i32(value: i32) -> Result<Permission, Error> {
    match value {
        59 => Ok(Permission::Execute),
        257 => Ok(Permission::Open),
        _ => Err(MetaError("unsupported value".to_string())),
    }
}

fn dec_from_i32(value: i32) -> Result<Decision, Error> {
    match value {
        0 => Err(MetaError("unknown decision 0".to_string())),
        1 => Ok(Decision::Allow),
        2 => Ok(Decision::Deny),
        _ => Err(MetaError("unsupported value".to_string())),
    }
}
