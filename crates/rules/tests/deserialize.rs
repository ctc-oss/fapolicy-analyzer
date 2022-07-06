use fapolicy_rules::read::deserialize_rules_db;
use std::error::Error;

#[test]
fn one_file_one_rule() -> Result<(), Box<dyn Error>> {
    let db = deserialize_rules_db(
        r#"
        [/foo.bar]
        allow perm=any all : all
        "#,
    )?;
    assert_eq!(db.len(), 1);
    assert_eq!(db.rules().len(), 1);
    assert!(db.rules().first().unwrap().valid);
    Ok(())
}

#[test]
fn one_file_two_rules() -> Result<(), Box<dyn Error>> {
    let db = deserialize_rules_db(
        r#"
        [/foo.bar]
        deny perm=execute all : all
        allow perm=any all : all
        "#,
    )?;
    assert_eq!(db.len(), 2);
    assert!(db.rules().iter().all(|r| r.origin == "foo.bar"));
    Ok(())
}

#[test]
fn two_files() -> Result<(), Box<dyn Error>> {
    let db = deserialize_rules_db(
        r#"
        [/foo.rules]
        allow perm=execute all : all
        [/bar.rules]
        allow perm=any all : all
        "#,
    )?;
    assert_eq!(db.len(), 2);
    assert_eq!(db.rules().len(), 2);
    Ok(())
}

#[test]
fn only_empty_file() -> Result<(), Box<dyn Error>> {
    let db = deserialize_rules_db(
        r#"
        [/foo.rules]
        "#,
    )?;
    assert!(db.is_empty());
    Ok(())
}

#[test]
fn leading_empty_file() -> Result<(), Box<dyn Error>> {
    let db = deserialize_rules_db(
        r#"
        [/foo.rules]
        [/bar.rules]
        allow perm=execute all : all
        "#,
    )?;
    assert_eq!(db.len(), 1);
    assert_eq!(db.rule(1).unwrap().origin, "bar.rules");
    Ok(())
}

#[test]
fn trailing_empty_file() -> Result<(), Box<dyn Error>> {
    let db = deserialize_rules_db(
        r#"
        [/foo.rules]
        allow perm=execute all : all
        [/bar.rules]
        "#,
    )?;
    assert_eq!(db.len(), 1);
    assert_eq!(db.rule(1).unwrap().origin, "foo.rules");
    Ok(())
}

#[test]
fn with_set() -> Result<(), Box<dyn Error>> {
    let db = deserialize_rules_db(
        r#"
        [/foo.bar]
        %foo=bar
        allow perm=any all : all
        "#,
    )?;
    assert_eq!(db.len(), 2);
    assert_eq!(db.rules().len(), 1);
    assert_eq!(db.sets().len(), 1);
    Ok(())
}
