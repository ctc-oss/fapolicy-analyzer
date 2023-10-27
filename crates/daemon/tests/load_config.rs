/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use assert_matches::assert_matches;
use fapolicy_daemon::conf::config::{Entry, IntegritySource, TrustBackend};
use fapolicy_daemon::conf::from_file;
use fapolicy_daemon::Config;

#[test]
fn parse_default_config() {
    let db = &from_file("tests/data/default.conf").expect("load");
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
}

#[test]
fn parse_empty_config() {
    let db = &from_file("tests/data/empty.conf").expect("load");
    assert!(db.is_empty());

    let x: Config = db.into();
    assert!(x.permissive.get().is_none());
    assert!(x.nice_val.get().is_none());
    assert!(x.q_size.get().is_none());
    assert!(x.uid.get().is_none());
    assert!(x.gid.get().is_none());
    assert!(x.do_stat_report.get().is_none());
    assert!(x.detailed_report.get().is_none());
    assert!(x.db_max_size.get().is_none());
    assert!(x.subj_cache_size.get().is_none());
    assert!(x.obj_cache_size.get().is_none());
    assert!(x.detailed_report.get().is_none());
    assert!(x.watch_fs.get().is_none());
    assert!(x.trust.get().is_none());
    assert!(x.integrity.get().is_none());
    assert!(x.syslog_format.get().is_none());
    assert!(x.rpm_sha256_only.get().is_none());
    assert!(x.allow_filesystem_mark.get().is_none());
}

#[test]
fn parse_bad_config() {
    let db = &from_file("tests/data/bad-values.conf").expect("load");
    let x: Config = db.into();
    assert_matches!(x.permissive, Entry::Invalid(str) if str == "true");

    // valid values will be parsed even with bad data present
    assert_matches!(x.db_max_size, Entry::Valid(50));
}

fn splits(s: &str) -> Vec<String> {
    s.split(',').map(String::from).collect::<Vec<_>>()
}
