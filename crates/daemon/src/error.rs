use thiserror::Error;

// errors that can occur in this crate
#[derive(Error, Debug)]
pub enum Error {
    #[error("{0}")]
    FapolicydReloadFail(String),
}
