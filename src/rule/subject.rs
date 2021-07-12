use std::fmt::{Display, Formatter};

#[derive(Clone, Debug, PartialEq)]
pub enum Subject {
    All,
    Uid(u32),
    Gid(u32),
    Exe(String),
    Pattern(String),
}

impl Display for Subject {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Subject::All => f.write_str("all"),
            Subject::Uid(id) => f.write_fmt(format_args!("uid={}", id)),
            Subject::Gid(id) => f.write_fmt(format_args!("gid={}", id)),
            Subject::Exe(id) => f.write_fmt(format_args!("exe={}", id)),
            Subject::Pattern(id) => f.write_fmt(format_args!("pattern={}", id)),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn display() {
        assert_eq!(format!("{}", Subject::All), "all");
        assert_eq!(format!("{}", Subject::Uid(42)), "uid=42");
        assert_eq!(format!("{}", Subject::Gid(42)), "gid=42");
    }
}
