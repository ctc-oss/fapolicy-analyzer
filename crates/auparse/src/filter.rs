use crate::record::Type;

pub type Filter = fn(Type) -> bool;
