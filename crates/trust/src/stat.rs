use fapolicy_api::trust::Trust;

/// Actual delivers metadata about the actual file that exists on the filesystem.
/// This is used to identify discrepancies between the trusted and the actual files.
#[derive(PartialEq, Eq, Clone, Debug)]
pub struct Actual {
    pub size: u64,
    pub hash: String,
    pub last_modified: u64,
}

/// Trust status tag
#[derive(Debug)]
pub enum Status {
    /// Filesystem matches trust
    Trusted(Trust, Actual),
    /// Filesystem does not match trust
    Discrepancy(Trust, Actual),
    /// Does not exist on filesystem
    Missing(Trust),
}
