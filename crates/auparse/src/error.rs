use std::time::SystemTimeError;
use thiserror::Error;

/// An error that can occur
#[derive(Error, Debug)]
pub enum Error {
    #[error("General failure: {0}")]
    GeneralFail(String),

    #[error("{0}")]
    DurationError(#[from] SystemTimeError),

    #[error("Failed to init auparse")]
    NativeInitFail,

    #[error("Native error {0}")]
    AuditParseError(#[from] auparse_sys::error::Error),
}
