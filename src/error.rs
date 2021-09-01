use crate::{rpm, sys, trust};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum Error {
    #[error("System error: {0}")]
    SystemError(#[from] sys::Error),

    #[error("Trust error: {0}")]
    TrustError(#[from] trust::Error),

    #[error("RPM error: {0}")]
    RpmError(#[from] rpm::Error),
}
