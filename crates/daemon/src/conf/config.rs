#[derive(Clone, Debug)]
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

#[derive(Clone, Debug)]
pub enum IntegritySource {
    None,
    Size,
    Hash,
}

#[derive(Clone)]
pub struct Config {
    pub permissive: bool,
    pub nice_val: usize,
    pub q_size: usize,
    pub uid: String,
    pub gid: String,
    pub do_stat_report: bool,
    pub detailed_report: bool,
    pub db_max_size: usize,
    pub subj_cache_size: usize,
    pub obj_cache_size: usize,
    pub watch_fs: Vec<String>,
    pub trust: Vec<TrustBackend>,
    pub integrity: IntegritySource,
    pub syslog_format: Vec<String>,
    pub rpm_sha256_only: bool,
    pub allow_filesystem_mark: bool,
}

#[derive(Debug)]
pub(crate) enum ConfigToken {
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

impl ConfigToken {
    pub fn apply(self, conf: &mut Config) {
        match self {
            ConfigToken::Permissive(v) => conf.permissive = v,
            ConfigToken::NiceVal(v) => conf.nice_val = v,
            ConfigToken::QSize(v) => conf.q_size = v,
            ConfigToken::UID(v) => conf.uid = v,
            ConfigToken::GID(v) => conf.gid = v,
            ConfigToken::DoStatReport(v) => conf.do_stat_report = v,
            ConfigToken::DetailedReport(v) => conf.detailed_report = v,
            ConfigToken::DbMaxSize(v) => conf.db_max_size = v,
            ConfigToken::SubjCacheSize(v) => conf.subj_cache_size = v,
            ConfigToken::ObjCacheSize(v) => conf.obj_cache_size = v,
            ConfigToken::WatchFs(v) => conf.watch_fs = v,
            ConfigToken::Trust(v) => conf.trust = v,
            ConfigToken::Integrity(v) => conf.integrity = v,
            ConfigToken::SyslogFormat(v) => conf.syslog_format = v,
            ConfigToken::RpmSha256Only(v) => conf.rpm_sha256_only = v,
            ConfigToken::AllowFsMark(v) => conf.allow_filesystem_mark = v,
        }
    }
}

impl Default for Config {
    fn default() -> Self {
        Self {
            permissive: false,
            nice_val: 14,
            q_size: 800,
            uid: "fapolicyd".to_string(),
            gid: "fapolicyd".to_string(),
            do_stat_report: true,
            detailed_report: true,
            db_max_size: 50,
            subj_cache_size: 1549,
            obj_cache_size: 8191,
            watch_fs: "ext2,ext3,ext4,tmpfs,xfs,vfat,iso9660,btrfs"
                .split(",")
                .map(|s| s.to_string())
                .collect(),
            trust: TrustBackend::defaults(),
            integrity: IntegritySource::None,
            syslog_format: "rule,dec,perm,auid,pid,exe,:,path,ftype,trust"
                .split(",")
                .map(|s| s.to_string())
                .collect(),
            rpm_sha256_only: false,
            allow_filesystem_mark: false,
        }
    }
}
