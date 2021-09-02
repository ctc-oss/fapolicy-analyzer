use crate::{rpm, sys, trust};
use std::io;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum Error {
    #[error("{0} not found: {1}")]
    FileNotFound(String, String),

    #[error("System error: {0}")]
    SystemError(#[from] sys::Error),

    #[error("Trust error: {0}")]
    TrustError(#[from] trust::Error),

    #[error("RPM error: {0}")]
    RpmError(#[from] rpm::Error),

    #[error("Hash error: {0}")]
    HashOpError(#[from] io::Error),
}
