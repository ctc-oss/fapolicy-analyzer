use crate::conf::config::Val::{Invalid, Valid};

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
pub enum Entry {
    Valid(),
    Invalid,
}

#[derive(Clone)]
pub struct Config {
    pub permissive: Val<bool>,
    pub nice_val: Val<usize>,
    pub q_size: Val<usize>,
    pub uid: Val<String>,
    pub gid: Val<String>,
    pub do_stat_report: Val<bool>,
    pub detailed_report: Val<bool>,
    pub db_max_size: Val<usize>,
    pub subj_cache_size: Val<usize>,
    pub obj_cache_size: Val<usize>,
    pub watch_fs: Val<Vec<String>>,
    pub trust: Val<Vec<TrustBackend>>,
    pub integrity: Val<IntegritySource>,
    pub syslog_format: Val<Vec<String>>,
    pub rpm_sha256_only: Val<bool>,
    pub allow_filesystem_mark: Val<bool>,
}

impl Config {
    pub fn empty() -> Self {
        Self {
            permissive: Val::Missing,
            nice_val: Val::Missing,
            q_size: Val::Missing,
            uid: Val::Missing,
            gid: Val::Missing,
            do_stat_report: Val::Missing,
            detailed_report: Val::Missing,
            db_max_size: Val::Missing,
            subj_cache_size: Val::Missing,
            obj_cache_size: Val::Missing,
            watch_fs: Val::Missing,
            trust: Val::Missing,
            integrity: Val::Missing,
            syslog_format: Val::Missing,
            rpm_sha256_only: Val::Missing,
            allow_filesystem_mark: Val::Missing,
        }
    }

    pub fn apply_ok(&mut self, tok: ConfigToken) {
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
pub enum Val<T> {
    Valid(T),
    Invalid(String),
    Missing,
}

impl<T> Val<T> {
    pub fn get(&self) -> Result<&T, ()> {
        match self {
            Valid(t) => Ok(t),
            _ => Err(()),
        }
    }
}

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
                    .split(",")
                    .map(|s| s.to_string())
                    .collect(),
            ),
            trust: Valid(TrustBackend::defaults()),
            integrity: Valid(IntegritySource::None),
            syslog_format: Valid(
                "rule,dec,perm,auid,pid,exe,:,path,ftype,trust"
                    .split(",")
                    .map(|s| s.to_string())
                    .collect(),
            ),
            rpm_sha256_only: Valid(false),
            allow_filesystem_mark: Valid(false),
        }
    }
}
