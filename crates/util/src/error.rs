use std::io;
use thiserror::Error;

/// An Error that can occur in this crate
#[derive(Error, Debug)]
pub enum Error {
    #[error("error generating hash, {0}")]
    HashingError(#[from] io::Error),
}
