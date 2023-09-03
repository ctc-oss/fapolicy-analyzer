use std::fmt::{Display, Formatter};

#[derive(Debug, Eq, PartialEq)]
pub enum Key {
    Permissive,
    NiceVal,
    QSize,
    UID,
    GID,
    DoStatReport,
    DetailedReport,
    DbMaxSize,
    SubjCacheSize,
    ObjCacheSize,
    WatchFs,
    Trust,
    Integrity,
    SyslogFormat,
    RpmSha256Only,
    AllowFsMark,
}

impl Display for Key {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        use Key::*;
        match self {
            Permissive => f.write_str("permissive"),
            NiceVal => f.write_str("nice_val"),
            QSize => f.write_str("q_size"),
            UID => f.write_str("uid"),
            GID => f.write_str("gid"),
            DoStatReport => f.write_str("do_stat_report"),
            DetailedReport => f.write_str("detailed_report"),
            DbMaxSize => f.write_str("db_max_size"),
            SubjCacheSize => f.write_str("subj_cache_size"),
            ObjCacheSize => f.write_str("obj_cache_size"),
            WatchFs => f.write_str("watch_fs"),
            Trust => f.write_str("trust"),
            Integrity => f.write_str("integrity"),
            SyslogFormat => f.write_str("syslog_format"),
            RpmSha256Only => f.write_str("rpm_sha256_only"),
            AllowFsMark => f.write_str("allow_filesystem_mark"),
        }
    }
}
