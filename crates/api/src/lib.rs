pub enum TrustSource {
    System,
    Ancillary,
}

pub trait Trust {
    fn size(self: &Self) -> i64;
    fn path(self: &Self) -> String;
    fn hash(self: &Self) -> String;
    fn source(self: &Self) -> TrustSource;
}
