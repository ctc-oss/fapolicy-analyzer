/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use fapolicy_daemon::conf::config::{IntegritySource, TrustBackend, ValError};
use fapolicy_daemon::conf::load;

#[test]
fn parse_default_config() -> Result<(), ValError> {
    let x = load::config("tests/data/default.conf").expect("load");
    assert!(!*x.permissive.get()?);
    assert_eq!(*x.nice_val.get()?, 14);
    assert_eq!(*x.q_size.get()?, 800);
    assert_eq!(*x.uid.get()?, "fapolicyd");
    assert_eq!(*x.gid.get()?, "fapolicyd");
    assert!(*x.do_stat_report.get()?);
    assert!(*x.detailed_report.get()?);
    assert_eq!(*x.db_max_size.get()?, 50);
    assert_eq!(*x.subj_cache_size.get()?, 1549);
    assert_eq!(*x.obj_cache_size.get()?, 8191);
    assert_eq!(
        *x.watch_fs.get()?,
        splits("ext2,ext3,ext4,tmpfs,xfs,vfat,iso9660,btrfs")
    );
    assert_eq!(*x.trust.get()?, vec![TrustBackend::Rpm, TrustBackend::File]);
    assert_eq!(*x.integrity.get()?, IntegritySource::None);
    assert_eq!(
        *x.syslog_format.get()?,
        splits("rule,dec,perm,auid,pid,exe,:,path,ftype,trust")
    );
    assert!(!*x.rpm_sha256_only.get()?);
    assert!(!*x.allow_filesystem_mark.get()?);

    Ok(())
}

fn splits(s: &str) -> Vec<String> {
    s.split(',').map(String::from).collect::<Vec<_>>()
}
