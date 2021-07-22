use std::fmt::{Display, Formatter};

use crate::rules::{parse, Rvalue};
use std::str::FromStr;

#[derive(Clone, Debug, PartialEq)]
pub struct Object {
    parts: Vec<Part>,
}

impl Object {
    pub fn new(parts: Vec<Part>) -> Self {
        Object { parts }
    }
}

#[derive(Clone, Debug, PartialEq)]
pub enum Part {
    All,
    Device(String),
    Dir(String),
    FileType(Rvalue),
    Path(String),
    Trust(bool),
}

impl From<Part> for Object {
    fn from(p: Part) -> Self {
        Object { parts: vec![p] }
    }
}

impl Display for Object {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let s: String = self
            .parts
            .iter()
            .map(|p| format!("{}", p))
            .collect::<Vec<String>>()
            .join(" ");
        f.write_fmt(format_args!("{}", s))
    }
}

impl Display for Part {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Part::All => f.write_str("all"),
            Part::Device(p) => f.write_fmt(format_args!("device={}", p)),
            Part::Dir(p) => f.write_fmt(format_args!("dir={}", p)),
            Part::FileType(t) => f.write_fmt(format_args!("ftype={}", t)),
            Part::Path(p) => f.write_fmt(format_args!("path={}", p)),
            Part::Trust(b) => f.write_fmt(format_args!("trust={}", bool_to_c(*b))),
        }
    }
}

fn bool_to_c(b: bool) -> char {
    if b {
        '1'
    } else {
        '0'
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
        assert_eq!(format!("{}", Part::All), "all");
        assert_eq!(format!("{}", Part::Dir("/foo".into())), "dir=/foo");
        assert_eq!(
            format!("{}", Part::Device("/dev/cdrom".into())),
            "device=/dev/cdrom"
        );
        assert_eq!(
            format!(
                "{}",
                Part::FileType(Literal("application/x-sharedlib".into()))
            ),
            "ftype=application/x-sharedlib"
        );
    }

    #[test]
    fn display_trusted() {
        assert_eq!(
            format!("{}", Object::new(vec![Part::All, Part::Trust(true)])),
            "all trust=1"
        );
        assert_eq!(
            format!(
                "{}",
                Object::new(vec![Part::Dir("/foo".into()), Part::Trust(true)])
            ),
            "dir=/foo trust=1"
        );
        assert_eq!(
            format!(
                "{}",
                Object::new(vec![Part::Device("/dev/cdrom".into()), Part::Trust(true)])
            ),
            "device=/dev/cdrom trust=1"
        );
        assert_eq!(
            format!(
                "{}",
                Object::new(vec![
                    Part::FileType(Literal("application/x-sharedlib".into())),
                    Part::Trust(true)
                ])
            ),
            "ftype=application/x-sharedlib trust=1"
        );
    }
}
