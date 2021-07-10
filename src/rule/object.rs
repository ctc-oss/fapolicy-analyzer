use std::fmt::{Display, Formatter};

use crate::rule::FileType;

pub enum Object {
    All,
    Dir(String),
    Device(String),
    FileType(FileType),
}

impl Display for Object {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Object::All => f.write_str("all"),
            Object::Dir(p) => f.write_fmt(format_args!("dir={}", p)),
            Object::Device(p) => f.write_fmt(format_args!("device={}", p)),
            Object::FileType(t) => f.write_fmt(format_args!("ftype={}", t)),
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
    fn object_display() {
        let ft1 = FileType("text/x-lua".into());

        assert_eq!(format!("{}", Object::All), "all");
        assert_eq!(format!("{}", Object::Dir("/foo".into())), "dir=/foo");
        assert_eq!(
            format!("{}", Object::Device("/dev/cdrom".into())),
            "device=/dev/cdrom"
        );
        assert_eq!(format!("{}", ft1), format!("ftype={}", &ft1.0));
    }
}
