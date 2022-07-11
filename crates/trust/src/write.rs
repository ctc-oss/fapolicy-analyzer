use crate::db::DB;
use std::fs::File;
use std::io::{Error, Write};
use std::path::PathBuf;

pub fn file_trust(db: &DB, to: PathBuf) -> Result<PathBuf, Error> {
    // write file trust db
    let mut tf = File::create(&to)?;
    for (path, meta) in db.iter() {
        if meta.is_ancillary() {
            tf.write_all(
                format!("{} {} {}\n", path, meta.trusted.size, meta.trusted.hash).as_bytes(),
            )?;
        }
    }
    Ok(to)
}
