use crate::rules::parse;
use std::fmt::{Display, Formatter};
use std::str::FromStr;

#[derive(Clone, Debug, PartialEq)]
pub enum Decision {
    Allow,
    Deny,
    DenyAudit,
}

impl Display for Decision {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Decision::Allow => f.write_str("allow"),
            Decision::Deny => f.write_str("deny"),
            Decision::DenyAudit => f.write_str("deny_audit"),
        }
    }
}

impl FromStr for Decision {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match parse::decision(s) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Decision from string".into()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn display() {
        assert_eq!(format!("{}", Decision::Allow), "allow");
        assert_eq!(format!("{}", Decision::Deny), "deny");
        assert_eq!(format!("{}", Decision::DenyAudit), "deny_audit");
    }
}
