#[derive(Clone)]
pub enum WatchFs {
    Ok(String),
    Bad(String),
}

impl WatchFs {
    fn defaults() -> Vec<Self> {
        vec![
            "ext2", "ext3", "ext4", "tmpfs", "xfs", "vfat", "iso9660", "btrfs",
        ]
        .iter()
        .map(|s| WatchFs::Ok(s.to_string()))
        .collect()
    }
}

#[derive(Clone)]
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

#[derive(Clone)]
pub enum IntegritySource {
    None,
    Size,
    Hash,
}

#[derive(Clone)]
pub struct Config {
    permissive: bool,
    nice_val: usize,
    q_size: usize,
    uid: String,
    gid: String,
    do_stat_report: bool,
    detailed_report: bool,
    db_max_size: usize,
    subj_cache_size: usize,
    obj_cache_size: usize,
    watch_fs: Vec<WatchFs>,
    trust: Vec<TrustBackend>,
    integrity: IntegritySource,
    syslog_format: String,
    rpm_sha256_only: bool,
    allow_filesystem_mark: bool,
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
            watch_fs: WatchFs::defaults(),
            trust: TrustBackend::defaults(),
            integrity: IntegritySource::None,
            syslog_format: "rule,dec,perm,auid,pid,exe,:,path,ftype,trust".to_string(),
            rpm_sha256_only: false,
            allow_filesystem_mark: false,
        }
    }
}
