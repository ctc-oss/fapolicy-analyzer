#[derive(Clone, Debug)]
pub enum TrustSource {
    System,
    Ancillary,
}

#[derive(Clone, Debug)]
pub struct Trust {
    pub path: String,
    pub size: u64,
    pub hash: Option<String>,
    pub source: TrustSource,
}

impl Trust {
    pub fn new(path: &str, size: u64, hash: &str, source: TrustSource) -> Trust {
        Trust {
            path: path.to_string(),
            size,
            hash: Some(hash.to_string()),
            source,
        }
    }
}
