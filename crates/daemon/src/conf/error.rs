use thiserror::Error;

#[derive(Error, Debug)]
pub enum Error {
    #[error("General config error")]
    General,
}
