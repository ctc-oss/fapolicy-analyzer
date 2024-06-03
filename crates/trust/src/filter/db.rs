use crate::filter::error::Error;

#[derive(Clone, Debug, Default)]
pub struct DB;

impl DB {
    pub fn from_file(path: &str) -> Result<DB, Error> {
        Ok(DB)
    }
}
