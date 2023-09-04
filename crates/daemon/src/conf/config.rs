/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::conf::key::Key;
use crate::conf::{Line, DB};
use std::fmt::{Display, Formatter};

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum TrustBackend {
    Rpm,
    File,
    Deb,
}

impl Display for TrustBackend {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            TrustBackend::Rpm => f.write_str("rpmdb"),
            TrustBackend::File => f.write_str("file"),
            TrustBackend::Deb => f.write_str("deb"),
        }
    }
}

impl TrustBackend {
    fn defaults() -> Vec<Self> {
        vec![Self::Rpm, Self::File]
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum IntegritySource {
    None,
    Size,
    Hash,
}

impl Display for IntegritySource {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            IntegritySource::None => f.write_str("none"),
            IntegritySource::Size => f.write_str("size"),
            IntegritySource::Hash => f.write_str("hash"),
        }
    }
}

#[derive(Clone)]
pub struct Config {
    pub permissive: Entry<bool>,
    pub nice_val: Entry<usize>,
    pub q_size: Entry<usize>,
    pub uid: Entry<String>,
    pub gid: Entry<String>,
    pub do_stat_report: Entry<bool>,
    pub detailed_report: Entry<bool>,
    pub db_max_size: Entry<usize>,
    pub subj_cache_size: Entry<usize>,
    pub obj_cache_size: Entry<usize>,
    pub watch_fs: Entry<Vec<String>>,
    pub trust: Entry<Vec<TrustBackend>>,
    pub integrity: Entry<IntegritySource>,
    pub syslog_format: Entry<Vec<String>>,
    pub rpm_sha256_only: Entry<bool>,
    pub allow_filesystem_mark: Entry<bool>,
}

impl From<&DB> for Config {
    fn from(value: &DB) -> Self {
        let mut cfg = Config::empty();
        for line in value.iter() {
            match line {
                Line::Valid(tok) => cfg.apply_ok(tok.clone()),
                Line::Invalid(tok, txt) => cfg.apply_err(tok, txt),
                Line::Duplicate(tok) => cfg.apply_ok(tok.clone()),
                _ => {}
            }
        }
        cfg
    }
}

impl Config {
    pub fn empty() -> Self {
        use Entry::Missing;
        Self {
            permissive: Missing,
            nice_val: Missing,
            q_size: Missing,
            uid: Missing,
            gid: Missing,
            do_stat_report: Missing,
            detailed_report: Missing,
            db_max_size: Missing,
            subj_cache_size: Missing,
            obj_cache_size: Missing,
            watch_fs: Missing,
            trust: Missing,
            integrity: Missing,
            syslog_format: Missing,
            rpm_sha256_only: Missing,
            allow_filesystem_mark: Missing,
        }
    }

    pub fn apply_ok(&mut self, tok: ConfigToken) {
        use ConfigToken::*;
        use Entry::Valid;
        match tok {
            Permissive(v) => self.permissive = Valid(v),
            NiceVal(v) => self.nice_val = Valid(v),
            QSize(v) => self.q_size = Valid(v),
            UID(v) => self.uid = Valid(v),
            GID(v) => self.gid = Valid(v),
            DoStatReport(v) => self.do_stat_report = Valid(v),
            DetailedReport(v) => self.detailed_report = Valid(v),
            DbMaxSize(v) => self.db_max_size = Valid(v),
            SubjCacheSize(v) => self.subj_cache_size = Valid(v),
            ObjCacheSize(v) => self.obj_cache_size = Valid(v),
            WatchFs(v) => self.watch_fs = Valid(v),
            Trust(v) => self.trust = Valid(v),
            Integrity(v) => self.integrity = Valid(v),
            SyslogFormat(v) => self.syslog_format = Valid(v),
            RpmSha256Only(v) => self.rpm_sha256_only = Valid(v),
            AllowFsMark(v) => self.allow_filesystem_mark = Valid(v),
        }
    }

    pub fn apply_err(&mut self, tok: &str, txt: &str) {
        use Entry::Invalid;
        match tok {
            "permissive" => self.permissive = Invalid(txt.to_string()),
            "nice_val" => self.nice_val = Invalid(txt.to_string()),
            "q_size" => self.q_size = Invalid(txt.to_string()),
            "uid" => self.uid = Invalid(txt.to_string()),
            "gid" => self.gid = Invalid(txt.to_string()),
            "do_stat_report" => self.do_stat_report = Invalid(txt.to_string()),
            "detailed_report" => self.detailed_report = Invalid(txt.to_string()),
            "db_max_size" => self.db_max_size = Invalid(txt.to_string()),
            "subj_cache_size" => self.subj_cache_size = Invalid(txt.to_string()),
            "obj_cache_size" => self.obj_cache_size = Invalid(txt.to_string()),
            "watch_fs" => self.watch_fs = Invalid(txt.to_string()),
            "trust" => self.trust = Invalid(txt.to_string()),
            "integrity" => self.integrity = Invalid(txt.to_string()),
            "syslog_format" => self.syslog_format = Invalid(txt.to_string()),
            "rpm_sha256_only" => self.rpm_sha256_only = Invalid(txt.to_string()),
            "allow_filesystem_mark" => self.allow_filesystem_mark = Invalid(txt.to_string()),
            _unsupported => {}
        }
    }
}

#[derive(Clone)]
pub enum Entry<T> {
    Valid(T),
    Invalid(String),
    Missing,
    Duplicated,
}

impl<T> Entry<T> {
    pub fn get(&self) -> Option<&T> {
        match self {
            Entry::Valid(v) => Some(v),
            _ => None,
        }
    }
}

#[derive(Clone, Debug)]
pub enum ConfigToken {
    Permissive(bool),
    NiceVal(usize),
    QSize(usize),
    UID(String),
    GID(String),
    DoStatReport(bool),
    DetailedReport(bool),
    DbMaxSize(usize),
    SubjCacheSize(usize),
    ObjCacheSize(usize),
    WatchFs(Vec<String>),
    Trust(Vec<TrustBackend>),
    Integrity(IntegritySource),
    SyslogFormat(Vec<String>),
    RpmSha256Only(bool),
    AllowFsMark(bool),
}

impl Default for Config {
    fn default() -> Self {
        use Entry::Valid;
        Self {
            permissive: Valid(false),
            nice_val: Valid(14),
            q_size: Valid(800),
            uid: Valid("fapolicyd".to_string()),
            gid: Valid("fapolicyd".to_string()),
            do_stat_report: Valid(true),
            detailed_report: Valid(true),
            db_max_size: Valid(50),
            subj_cache_size: Valid(1549),
            obj_cache_size: Valid(8191),
            watch_fs: Valid(
                "ext2,ext3,ext4,tmpfs,xfs,vfat,iso9660,btrfs"
                    .split(',')
                    .map(|s| s.to_string())
                    .collect(),
            ),
            trust: Valid(TrustBackend::defaults()),
            integrity: Valid(IntegritySource::None),
            syslog_format: Valid(
                "rule,dec,perm,auid,pid,exe,:,path,ftype,trust"
                    .split(',')
                    .map(|s| s.to_string())
                    .collect(),
            ),
            rpm_sha256_only: Valid(false),
            allow_filesystem_mark: Valid(false),
        }
    }
}

fn bstr(b: &bool) -> &str {
    if *b {
        "1"
    } else {
        "0"
    }
}

impl Display for ConfigToken {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        use ConfigToken::*;
        match self {
            Permissive(v) => f.write_fmt(format_args!("{}={}", Key::Permissive, bstr(v))),
            NiceVal(v) => f.write_fmt(format_args!("{}={}", Key::NiceVal, v)),
            QSize(v) => f.write_fmt(format_args!("{}={}", Key::QSize, v)),
            UID(v) => f.write_fmt(format_args!("{}={}", Key::UID, v)),
            GID(v) => f.write_fmt(format_args!("{}={}", Key::GID, v)),
            DoStatReport(v) => f.write_fmt(format_args!("{}={}", Key::DoStatReport, bstr(v))),
            DetailedReport(v) => f.write_fmt(format_args!("{}={}", Key::DetailedReport, bstr(v))),
            DbMaxSize(v) => f.write_fmt(format_args!("{}={}", Key::DbMaxSize, v)),
            SubjCacheSize(v) => f.write_fmt(format_args!("{}={}", Key::SubjCacheSize, v)),
            ObjCacheSize(v) => f.write_fmt(format_args!("{}={}", Key::ObjCacheSize, v)),
            WatchFs(v) => f.write_fmt(format_args!("{}={}", Key::WatchFs, v.join(","))),
            Trust(v) => f.write_fmt(format_args!(
                "{}={}",
                Key::Trust,
                v.iter()
                    .map(|v| v.to_string())
                    .collect::<Vec<String>>()
                    .join(",")
            )),
            Integrity(v) => f.write_fmt(format_args!("{}={}", Key::Integrity, v)),
            SyslogFormat(v) => f.write_fmt(format_args!("{}={}", Key::SyslogFormat, v.join(","))),
            RpmSha256Only(v) => f.write_fmt(format_args!("{}={}", Key::RpmSha256Only, bstr(v))),
            AllowFsMark(v) => f.write_fmt(format_args!("{}={}", Key::AllowFsMark, bstr(v))),
        }
    }
}
