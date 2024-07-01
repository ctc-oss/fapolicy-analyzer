use crate::filter::DB;
use std::fs::File;
use std::io;
use std::io::Write;
use std::path::Path;

pub fn db(db: &DB, to: &Path) -> Result<(), io::Error> {
    let mut conf_file = File::create(to)?;
    for line in db.iter() {
        conf_file.write_all(format!("{}\n", line).as_bytes())?;
    }
    Ok(())
}
