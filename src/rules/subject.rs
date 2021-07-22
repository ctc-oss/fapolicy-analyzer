use std::fmt::{Display, Formatter};
use std::str::FromStr;

use crate::rules::{bool_to_c, parse};

#[derive(Clone, Debug, PartialEq)]
pub struct Subject {
    parts: Vec<Part>,
}

impl Subject {
    pub fn new(parts: Vec<Part>) -> Self {
        Subject { parts }
    }
}

#[derive(Clone, Debug, PartialEq)]
pub enum Part {
    All,
    Comm(String),
    Uid(u32),
    Gid(u32),
    Exe(String),
    Pattern(String),
    Trust(bool),
}

impl From<Part> for Subject {
    fn from(p: Part) -> Self {
        Subject { parts: vec![p] }
    }
}

impl Display for Subject {
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
            Part::Comm(cmd) => f.write_fmt(format_args!("comm={}", cmd)),
            Part::Uid(id) => f.write_fmt(format_args!("uid={}", id)),
            Part::Gid(id) => f.write_fmt(format_args!("gid={}", id)),
            Part::Exe(id) => f.write_fmt(format_args!("exe={}", id)),
            Part::Pattern(id) => f.write_fmt(format_args!("pattern={}", id)),
            Part::Trust(b) => f.write_fmt(format_args!("trust={}", bool_to_c(*b))),
        }
    }
}

impl FromStr for Subject {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match parse::subject(s) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Subject from string".into()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn display() {
        assert_eq!(format!("{}", Part::All), "all");
        assert_eq!(format!("{}", Part::Comm("dnf".into())), "comm=dnf");
        assert_eq!(format!("{}", Part::Uid(42)), "uid=42");
        assert_eq!(format!("{}", Part::Gid(42)), "gid=42");
        assert_eq!(format!("{}", Part::Trust(false)), "trust=0");
        assert_eq!(format!("{}", Part::Trust(true)), "trust=1");
    }

    #[test]
    fn fromstr() -> Result<(), String> {
        assert_eq!(Subject::from(Part::All), Subject::from_str("all")?);
        assert_eq!(
            Subject::from(Part::Comm("dnf".into())),
            Subject::from_str("comm=dnf")?
        );
        assert_eq!(Subject::from(Part::Uid(42)), Subject::from_str("uid=42")?);
        assert_eq!(Subject::from(Part::Gid(42)), Subject::from_str("gid=42")?);
        assert_eq!(
            Subject::from(Part::Trust(true)),
            Subject::from_str("trust=1")?
        );
        assert_eq!(
            Subject::from(Part::Trust(false)),
            Subject::from_str("trust=0")?
        );
        Ok(())
    }
}
