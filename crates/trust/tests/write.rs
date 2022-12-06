use fapolicy_trust::db::{Rec, DB};
use fapolicy_trust::source::TrustSource::DFile;
use fapolicy_trust::write;
use std::error::Error;
use std::fs::File;
use std::io::{BufReader, Read};
use std::path::Path;
use std::{fs, io};
use tempfile::NamedTempFile;

#[test]
fn test_dir_single_file() -> Result<(), Box<dyn Error>> {
    let mut db = DB::new();
    let expected = r#"/foo 0 0000000000"#;

    let mut rec: Rec = expected.parse()?;
    rec.source = Some(DFile("test-00.trust".to_string()));
    db.put(rec);

    let etc_fapolicyd = tempfile::tempdir()?.into_path();
    let trust_d = tempfile::tempdir_in(&etc_fapolicyd)?.into_path();
    let trust_f = etc_fapolicyd.join("fapolicyd.trust");
    write::db(&db, &trust_d, Some(&trust_f))?;

    let expected_file = trust_d.join("test-00.trust");
    let actual = read_string(&expected_file)?;
    assert_eq!(expected, actual.trim());

    Ok(())
}

#[test]
fn test_dir_and_file() -> Result<(), Box<dyn Error>> {
    let mut db = DB::new();
    let expected1 = r#"/foo 0 0000000000"#;
    let expected2 = r#"/bar 0 0000000000"#;

    let mut rec1: Rec = expected1.parse()?;
    rec1.source = Some(DFile("test-00.trust".to_string()));
    db.put(rec1);
    db.put(expected2.parse()?);

    let etc_fapolicyd = tempfile::tempdir()?.into_path();
    let trust_d = tempfile::tempdir_in(&etc_fapolicyd)?.into_path();
    let trust_f = etc_fapolicyd.join("fapolicyd.trust");
    write::db(&db, &trust_d, Some(&trust_f))?;

    let expected_file = trust_d.join("test-00.trust");
    let actual = read_string(&expected_file)?;
    assert_eq!(expected1, actual.trim());

    let actual = read_string(&trust_f)?;
    assert_eq!(expected2, actual.trim());

    Ok(())
}

#[test]
fn proper_file_count() -> Result<(), Box<dyn Error>> {
    let mut db = DB::new();

    let mut rec: Rec = "/foo 0 00000000".parse()?;
    rec.source = Some(DFile("00.trust".to_string()));
    db.put(rec);

    let mut rec: Rec = "/bar 0 00000000".parse()?;
    rec.source = Some(DFile("00.trust".to_string()));
    db.put(rec);

    let mut rec: Rec = "/baz 0 00000000".parse()?;
    rec.source = Some(DFile("00.trust".to_string()));
    db.put(rec);

    let etc_fapolicyd = tempfile::tempdir()?.into_path();
    let trust_d = tempfile::tempdir_in(&etc_fapolicyd)?.into_path();
    let trust_f = etc_fapolicyd.join("fapolicyd.trust");
    write::db(&db, &trust_d, Some(&trust_f))?;

    assert_eq!(fs::read_dir(trust_d)?.count(), 1);

    Ok(())
}

#[test]
fn test_dir_and_file_overwrite_1() -> Result<(), Box<dyn Error>> {
    let mut db = DB::new();

    let expected = "/foo 0 00000000";

    // foo get added from 00.trust
    let mut rec: Rec = expected.parse()?;
    rec.source = Some(DFile("00.trust".to_string()));
    db.put(rec);

    // foo gets added later with no source
    let mut rec: Rec = expected.parse()?;
    rec.source = None;
    db.put(rec);

    let etc_fapolicyd = tempfile::tempdir()?.into_path();
    let trust_d = tempfile::tempdir_in(&etc_fapolicyd)?.into_path();
    let trust_f = etc_fapolicyd.join("fapolicyd.trust");
    write::db(&db, &trust_d, Some(&trust_f))?;

    // trust file should contain the foo entry
    let trust_f = etc_fapolicyd.join("fapolicyd.trust");
    let actual = read_string(&trust_f)?;
    assert_eq!(expected, actual.trim());

    // should be no trust.d entries
    assert_eq!(fs::read_dir(trust_d)?.count(), 0);

    Ok(())
}

#[test]
fn test_dir_and_file_overwrite_2() -> Result<(), Box<dyn Error>> {
    let mut db = DB::new();

    let expected = "/foo 0 00000000";

    // foo gets added with no source
    let mut rec: Rec = expected.parse()?;
    rec.source = None;
    db.put(rec);

    // foo get added later from 00.trust
    let mut rec: Rec = expected.parse()?;
    rec.source = Some(DFile("00.trust".to_string()));
    db.put(rec);

    let etc_fapolicyd = tempfile::tempdir()?.into_path();
    let trust_d = tempfile::tempdir_in(&etc_fapolicyd)?.into_path();
    let trust_f = NamedTempFile::new_in(&etc_fapolicyd)?;
    write::db(&db, &trust_d, Some(trust_f.path()))?;

    // should be one trust.d entries and trust file should exist
    assert_eq!(fs::read_dir(&trust_d)?.count(), 1);
    assert!(trust_f.path().exists());

    // 00 trust should contain the foo entry
    let trust_00 = trust_d.join("00.trust");
    let actual = read_string(&trust_00)?;
    assert_eq!(expected, actual.trim());

    // trust file should be empty
    let actual = read_string(trust_f.path())?;
    assert!(actual.is_empty());

    Ok(())
}

fn read_string(from: &Path) -> Result<String, io::Error> {
    let mut reader = File::open(&from).map(BufReader::new)?;
    let mut actual = String::new();
    reader.read_to_string(&mut actual)?;
    Ok(actual)
}
