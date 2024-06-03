use crate::filter::db::DB;
use crate::filter::error::Error;

pub fn mem(txt: &str) -> Result<DB, Error> {
    Ok(DB)
}
