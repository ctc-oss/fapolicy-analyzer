use std::fmt::{Display, Formatter};
use std::str::FromStr;

use serde::Deserialize;
use serde::Serialize;

use crate::users::parse;

/// # User
/// Represents a /etc/passwd User
///
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct User {
    pub name: String,
    pub uid: u32,
    pub gid: u32,
    pub home: String,
    pub shell: String,
}

impl Display for User {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.write_fmt(format_args!(
            "{}:x:{}:{}:{}:{}:{}",
            self.name, self.uid, self.gid, self.name, self.home, self.shell
        ))
    }
}

impl FromStr for User {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match parse::user(s) {
            Ok((_, u)) => Ok(u),
            Err(_) => Err("Failed to parse User from string".into()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn testuser() -> User {
        User {
            name: "daemon".into(),
            uid: 1,
            gid: 1,
            home: "/usr/sbin".into(),
            shell: "/usr/sbin/nologin".into(),
        }
    }

    #[test]
    fn display() {
        assert_eq!(
            format!("{}", testuser()),
            "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin"
        );
    }

    #[test]
    fn fromstr() {
        let actual = User::from_str("daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin").unwrap();
        assert_eq!(testuser(), actual);
    }

    #[test]
    fn without_comment_field() {
        let actual = User::from_str("daemon:x:1:1::/usr/sbin:/usr/sbin/nologin").unwrap();
        assert_eq!(testuser(), actual);
    }
}
