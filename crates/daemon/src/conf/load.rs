use crate::conf::error::Error;
use crate::conf::read;
use crate::Config;

pub fn config(path: &str) -> Result<Config, Error> {
    read::file(path.into())
}
