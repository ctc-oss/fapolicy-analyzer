use std::fmt::{Display, Formatter};

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
