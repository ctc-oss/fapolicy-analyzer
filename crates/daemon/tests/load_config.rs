/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use fapolicy_daemon::conf::config::{IntegritySource, TrustBackend};
use fapolicy_daemon::conf::load;
use fapolicy_daemon::Config;
use std::error::Error;

#[test]
fn parse_default_config() -> Result<(), Box<dyn Error>> {
    let db = &load::file("tests/data/default.conf").expect("load");
    let x: Config = db.into();
    assert!(!x.permissive.get().unwrap());
    assert_eq!(*x.nice_val.get().unwrap(), 14);
    assert_eq!(*x.q_size.get().unwrap(), 800);
    assert_eq!(*x.uid.get().unwrap(), "fapolicyd");
    assert_eq!(*x.gid.get().unwrap(), "fapolicyd");
    assert!(*x.do_stat_report.get().unwrap());
    assert!(*x.detailed_report.get().unwrap());
    assert_eq!(*x.db_max_size.get().unwrap(), 50);
    assert_eq!(*x.subj_cache_size.get().unwrap(), 1549);
    assert_eq!(*x.obj_cache_size.get().unwrap(), 8191);
    assert_eq!(
        *x.watch_fs.get().unwrap(),
        splits("ext2,ext3,ext4,tmpfs,xfs,vfat,iso9660,btrfs")
    );
    assert_eq!(
        *x.trust.get().unwrap(),
        vec![TrustBackend::Rpm, TrustBackend::File]
    );
    assert_eq!(*x.integrity.get().unwrap(), IntegritySource::None);
    assert_eq!(
        *x.syslog_format.get().unwrap(),
        splits("rule,dec,perm,auid,pid,exe,:,path,ftype,trust")
    );
    assert!(!x.rpm_sha256_only.get().unwrap());
    assert!(!x.allow_filesystem_mark.get().unwrap());

    Ok(())
}

fn splits(s: &str) -> Vec<String> {
    s.split(',').map(String::from).collect::<Vec<_>>()
}
