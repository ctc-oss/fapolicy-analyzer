/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum TrustBackend {
    Rpm,
    File,
    Deb,
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

impl Config {
    pub fn empty() -> Self {
        Self {
            permissive: Entry::Missing,
            nice_val: Entry::Missing,
            q_size: Entry::Missing,
            uid: Entry::Missing,
            gid: Entry::Missing,
            do_stat_report: Entry::Missing,
            detailed_report: Entry::Missing,
            db_max_size: Entry::Missing,
            subj_cache_size: Entry::Missing,
            obj_cache_size: Entry::Missing,
            watch_fs: Entry::Missing,
            trust: Entry::Missing,
            integrity: Entry::Missing,
            syslog_format: Entry::Missing,
            rpm_sha256_only: Entry::Missing,
            allow_filesystem_mark: Entry::Missing,
        }
    }

    pub fn apply_ok(&mut self, tok: ConfigToken) {
        use Entry::Valid;
        match tok {
            ConfigToken::Permissive(v) => self.permissive = Valid(v),
            ConfigToken::NiceVal(v) => self.nice_val = Valid(v),
            ConfigToken::QSize(v) => self.q_size = Valid(v),
            ConfigToken::UID(v) => self.uid = Valid(v),
            ConfigToken::GID(v) => self.gid = Valid(v),
            ConfigToken::DoStatReport(v) => self.do_stat_report = Valid(v),
            ConfigToken::DetailedReport(v) => self.detailed_report = Valid(v),
            ConfigToken::DbMaxSize(v) => self.db_max_size = Valid(v),
            ConfigToken::SubjCacheSize(v) => self.subj_cache_size = Valid(v),
            ConfigToken::ObjCacheSize(v) => self.obj_cache_size = Valid(v),
            ConfigToken::WatchFs(v) => self.watch_fs = Valid(v),
            ConfigToken::Trust(v) => self.trust = Valid(v),
            ConfigToken::Integrity(v) => self.integrity = Valid(v),
            ConfigToken::SyslogFormat(v) => self.syslog_format = Valid(v),
            ConfigToken::RpmSha256Only(v) => self.rpm_sha256_only = Valid(v),
            ConfigToken::AllowFsMark(v) => self.allow_filesystem_mark = Valid(v),
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

#[derive(Debug)]
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
