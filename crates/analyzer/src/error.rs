use std::io;

use thiserror::Error;

#[derive(Error, Debug)]
pub enum Error {
    #[error("{0} not found: {1}")]
    FileNotFound(String, String),

    #[error("Trust error: {0}")]
    TrustError(#[from] fapolicy_trust::error::Error),

    #[error("File IO Error: {0}")]
    FileIoError(#[from] io::Error),

    #[error("Error reading metadata: {0}")]
    MetaError(String),

    #[error("{0}")]
    GeneralError(#[from] fapolicy_util::error::Error),
}
