use std::time::SystemTimeError;
use thiserror::Error;

/// An error that can occur
#[derive(Error, Debug)]
pub enum Error {
    #[error("Failed to get field {0}")]
    GetAuditFieldFail(String),
}
