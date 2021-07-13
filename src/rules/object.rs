use std::fmt::{Display, Formatter};

use crate::rules::{parse, FileType};
use std::str::FromStr;

#[derive(Clone, Debug, PartialEq)]
pub enum Object {
    All,
    Dir(String),
    Device(String),
    FileType(FileType),
}

impl Display for Object {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Object::All => f.write_str("all"),
            Object::Dir(p) => f.write_fmt(format_args!("dir={}", p)),
            Object::Device(p) => f.write_fmt(format_args!("device={}", p)),
            Object::FileType(t) => f.write_fmt(format_args!("ftype={}", t)),
        }
    }
}

impl FromStr for Object {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match parse::object(s) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Object to string".into()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn display() {
        assert_eq!(format!("{}", Object::All), "all");
        assert_eq!(format!("{}", Object::Dir("/foo".into())), "dir=/foo");
        assert_eq!(
            format!("{}", Object::Device("/dev/cdrom".into())),
            "device=/dev/cdrom"
        );
    }
}
