use thiserror::Error;

// errors that can occur in this crate
#[derive(Error, Debug)]
pub enum Error {
    #[error("{0}")]
    FapolicydReloadFail(String),

    #[cfg(feature = "systemd")]
    #[error("dbus {0}")]
    DbusFailure(#[from] dbus::Error),

    #[cfg(feature = "systemd")]
    #[error("dbus method-call {0}")]
    DbusMethodCall(String),
}
