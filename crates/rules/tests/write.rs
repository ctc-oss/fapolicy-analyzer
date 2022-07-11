/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use fapolicy_rules::{read, write};
use std::error::Error;
use std::fs::{read_dir, File};
use std::io;
use std::io::{BufReader, Read};
use std::path::Path;
use tempfile::NamedTempFile;

#[test]
fn test_file() -> Result<(), Box<dyn Error>> {
    let expected = r#"allow perm=any all : all"#;
    let db = read::deserialize_rules_db(expected)?;
    let file = NamedTempFile::new()?;

    write::db(&db, &file.path().to_path_buf())?;
    let actual = read_string(&file.path().to_path_buf())?;
    assert_eq!(expected, actual.trim());

    Ok(())
}

#[test]
fn test_dir_anon_file() -> Result<(), Box<dyn Error>> {
    let expected = r#"allow perm=any all : all"#;
    let db = read::deserialize_rules_db(expected)?;

    let etc_fapolicyd = tempfile::tempdir()?.into_path();
    let rules_d = tempfile::tempdir_in(etc_fapolicyd)?.into_path();
    write::db(&db, &rules_d)?;

    for f in read_dir(rules_d)? {
        let actual = read_string(&f.unwrap().path())?;
        assert_eq!(expected, actual.trim());
    }

    Ok(())
}

#[test]
fn test_dir_single_file() -> Result<(), Box<dyn Error>> {
    let expected = "allow perm=any all : all";
    let db = read::deserialize_rules_db(&format!(
        r#"
    [foo.rules]
    {}
    "#,
        expected
    ))?;

    let etc_fapolicyd = tempfile::tempdir()?.into_path();
    let rules_d = tempfile::tempdir_in(&etc_fapolicyd)?.into_path();
    write::db(&db, &rules_d)?;

    for f in read_dir(rules_d)? {
        let actual = read_string(&f.unwrap().path())?;
        assert_eq!(expected, actual.trim());
    }

    let compiled = read_string(&etc_fapolicyd.join("compiled.rules"))?;
    assert_eq!(compiled, format!("{}\n", expected));

    Ok(())
}

#[test]
fn test_dir_multi_file() -> Result<(), Box<dyn Error>> {
    let expected0 = "allow perm=exec all : all";
    let expected1 = "allow perm=any all : all";
    let db = read::deserialize_rules_db(&format!(
        r#"
    [00-foo.rules]
    {}
    [01-bar.rules]
    {}
    "#,
        expected0, expected1
    ))?;

    let etc_fapolicyd = tempfile::tempdir()?.into_path();
    let rules_d = tempfile::tempdir_in(&etc_fapolicyd)?.into_path();
    write::db(&db, &rules_d)?;

    let expected = vec![expected0, expected1];
    for (i, f) in read_dir(rules_d)?.enumerate() {
        let actual = read_string(&f.unwrap().path())?.trim();
        println!("{}: expected [{}], actual[{}]", i, expected[i], actual);
        assert_eq!(expected[i], actual);
    }

    let compiled = read_string(&etc_fapolicyd.join("compiled.rules"))?;
    assert_eq!(compiled, format!("{}\n{}\n", expected0, expected1));

    Ok(())
}

#[test]
fn test_dir_multi_file_multi_rule() -> Result<(), Box<dyn Error>> {
    let expected0 = "allow perm=any uid=0 : all";
    let expected1 = "allow perm=exec all : all";
    let expected2 = "deny perm=any all : all";
    let db = read::deserialize_rules_db(&format!(
        r#"
    [00-foo.rules]
    {}
    {}
    [01-bar.rules]
    {}
    "#,
        expected0, expected1, expected2
    ))?;

    let etc_fapolicyd = tempfile::tempdir()?.into_path();
    let rules_d = tempfile::tempdir_in(&etc_fapolicyd)?.into_path();
    write::db(&db, &rules_d)?;

    let concat = format!("{}\n{}", expected0, expected1);
    let expected = vec![concat.as_str(), expected2];
    for (i, f) in read_dir(rules_d)?.enumerate() {
        let actual = read_string(&f.unwrap().path())?.trim();
        println!("{}: expected [{}], actual[{}]", i, expected[i], actual);
        assert_eq!(expected[i], actual);
    }

    let compiled = read_string(&etc_fapolicyd.join("compiled.rules"))?;
    assert_eq!(
        compiled,
        format!("{}\n{}\n{}\n", expected0, expected1, expected2)
    );

    Ok(())
}

fn read_string(from: &Path) -> Result<String, io::Error> {
    let mut reader = File::open(&from).map(BufReader::new)?;
    let mut actual = String::new();
    reader.read_to_string(&mut actual)?;
    Ok(actual)
}
