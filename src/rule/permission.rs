use std::fmt::{Display, Formatter};

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

    //deny_audit perm=any all                : device=/dev/cdrom
    //deny_audit perm=execute all            : ftype=any
    //deny_audit perm=open exe=/usr/bin/ssh : dir=/opt
    //deny_audit perm=any pattern=ld_so : all

    #[test]
    fn display() {
        assert_eq!(format!("{}", Permission::Any), "perm=any");
        assert_eq!(format!("{}", Permission::Open), "perm=open");
        assert_eq!(format!("{}", Permission::Execute), "perm=execute");
    }
}
