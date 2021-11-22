use std::io;

use thiserror::Error;

#[derive(Error, Debug)]
pub enum Error {
    #[error("File IO Error: {0}")]
    FileIoError(#[from] io::Error),
}
