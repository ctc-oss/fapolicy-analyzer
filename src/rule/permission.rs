use std::fmt::{Display, Formatter};

#[derive(Clone, Debug, PartialEq)]
pub enum Permission {
    Any,
    Open,
    Execute,
}

impl Display for Permission {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.write_str("perm=")?;
        match self {
            Permission::Any => f.write_str("any"),
            Permission::Open => f.write_str("open"),
            Permission::Execute => f.write_str("execute"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn display() {
        assert_eq!(format!("{}", Permission::Any), "perm=any");
        assert_eq!(format!("{}", Permission::Open), "perm=open");
        assert_eq!(format!("{}", Permission::Execute), "perm=execute");
    }
}
