use auparse_sys::*;

#[derive(Debug, PartialEq)]
pub enum Type {
    Unknown(u32),
    Cwd,
    Fanotify,
    Path,
    Proctitle,
    Syscall,
    SystemBoot,
}

impl From<u32> for Type {
    fn from(v: u32) -> Self {
        use Type::*;
        match v {
            AUDIT_SYSCALL => Syscall,
            AUDIT_CWD => Cwd,
            AUDIT_FANOTIFY => Fanotify,
            AUDIT_PATH => Path,
            AUDIT_PROCTITLE => Proctitle,
            AUDIT_SYSTEM_BOOT => SystemBoot,
            _ => Unknown(v),
        }
    }
}

impl From<Type> for u32 {
    fn from(t: Type) -> Self {
        use Type::*;
        match t {
            Unknown(v) => v,
            Cwd => AUDIT_CWD,
            Fanotify => AUDIT_FANOTIFY,
            Path => AUDIT_PATH,
            Proctitle => AUDIT_PROCTITLE,
            Syscall => AUDIT_SYSCALL,
            SystemBoot => AUDIT_SYSTEM_BOOT,
        }
    }
}
