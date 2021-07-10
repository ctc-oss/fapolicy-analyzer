use std::fmt::{Display, Formatter};

pub enum Subject {
    All,
    Uid(u32),
    Gid(u32),
}

impl Display for Subject {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Subject::All => f.write_str("all"),
            Subject::Uid(id) => f.write_fmt(format_args!("uid={}", id)),
            Subject::Gid(id) => f.write_fmt(format_args!("gid={}", id)),
        }
    }
}
