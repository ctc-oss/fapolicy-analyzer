use std::fmt::{Display, Formatter};

use crate::rules::object::Object::{Trusted, Untrusted};
use crate::rules::{parse, Rvalue};
use std::str::FromStr;

#[derive(Clone, Debug, PartialEq)]
pub enum Object {
    All,
    Device(String),
    Dir(String),
    FileType(Rvalue),
    Path(String),
    Trusted(Box<Object>),
    Untrusted(Box<Object>),
}

impl Object {
    pub fn with_trust(o: &Object, t: bool) -> Object {
        if t {
            Trusted(Box::new(o.clone()))
        } else {
            Untrusted(Box::new(o.clone()))
        }
    }
}

impl Display for Object {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Object::All => f.write_str("all"),
            Object::Device(p) => f.write_fmt(format_args!("device={}", p)),
            Object::Dir(p) => f.write_fmt(format_args!("dir={}", p)),
            Object::FileType(t) => f.write_fmt(format_args!("ftype={}", t)),
            Object::Path(p) => f.write_fmt(format_args!("path={}", p)),
            Object::Trusted(o) => f.write_fmt(format_args!("{} trust=1", o)),
            Object::Untrusted(o) => f.write_fmt(format_args!("{} trust=0", o)),
        }
    }
}

impl FromStr for Object {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match parse::object(s) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Object from string".into()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::rules::file_type::Rvalue::Literal;

    #[test]
    fn display() {
        assert_eq!(format!("{}", Object::All), "all");
        assert_eq!(format!("{}", Object::Dir("/foo".into())), "dir=/foo");
        assert_eq!(
            format!("{}", Object::Device("/dev/cdrom".into())),
            "device=/dev/cdrom"
        );
        assert_eq!(
            format!(
                "{}",
                Object::FileType(Literal("application/x-sharedlib".into()))
            ),
            "ftype=application/x-sharedlib"
        );
    }

    #[test]
    fn display_trusted() {
        assert_eq!(
            format!("{}", Object::Trusted(Box::new(Object::All))),
            "all trust=1"
        );
        assert_eq!(
            format!("{}", Object::Trusted(Box::new(Object::Dir("/foo".into())))),
            "dir=/foo trust=1"
        );
        assert_eq!(
            format!(
                "{}",
                Object::Trusted(Box::new(Object::Device("/dev/cdrom".into())))
            ),
            "device=/dev/cdrom trust=1"
        );
        assert_eq!(
            format!(
                "{}",
                Trusted(Box::new(Object::FileType(Literal(
                    "application/x-sharedlib".into()
                ))))
            ),
            "ftype=application/x-sharedlib trust=1"
        );
    }
}
