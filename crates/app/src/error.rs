use confy::ConfyError;
use thiserror::Error;

use crate::sys;

/// An Error that can occur in this crate
#[derive(Error, Debug)]
pub enum Error {
    #[error("System error: {0}")]
    SystemError(#[from] sys::Error),
    #[error("Trust error: {0}")]
    TrustError(#[from] fapolicy_trust::error::Error),
    #[error("Analyzer error: {0}")]
    AnalyzerError(#[from] fapolicy_analyzer::error::Error),
    #[error("XDG config error: {0}")]
    ConfigError(#[from] ConfyError),
}
