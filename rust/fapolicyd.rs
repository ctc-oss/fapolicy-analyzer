// todo;; tracking the fapolicyd specific bits in here to determine if bindings are worthwhile

use std::io::Write;

pub const TRUST_DB_PATH: &str = "/var/lib/fapolicyd";
pub const TRUST_FILE_PATH: &str = "/etc/fapolicyd/fapolicyd.trust";
pub const RPM_DB_PATH: &str = "/var/lib/rpm";
pub const FIFO_PIPE: &str = "/run/fapolicyd/fapolicyd.fifo";

const USR_SHARE_ALLOWED_EXTS: [&str; 15] = [
    "pyc", "pyo", "py", "rb", "pl", "stp", "js", "jar", "m4", "php", "el", "pm", "lua", "class",
    "elc",
];

/// send signal to fapolicyd FIFO pipe to reload the trust database
pub fn reload_databases() {
    std::fs::OpenOptions::new()
        .write(true)
        .read(false)
        .open(FIFO_PIPE)
        .expect("unable to open fifo pipe")
        .write_all("1".as_bytes())
        .expect("unable to write fifo pipe");
}

/// filtering logic as implemented by fapolicyd rpm backend
pub fn keep_entry(p: &str) -> bool {
    match p {
        s if s.starts_with("/usr/share") => {
            USR_SHARE_ALLOWED_EXTS.iter().any(|ext| s.ends_with(*ext)) || s.contains("/libexec/")
        }
        s if s.starts_with("/usr/src") => s.contains("/scripts/") || s.contains("/tools/objtool/"),
        s if s.starts_with("/usr/include") => false,
        _ => true,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn drop_entry(path: &str) -> bool {
        !keep_entry(path)
    }

    #[test]
    fn test_drop_path() {
        // keep entries from /usr/share that are approved ext
        assert!(keep_entry("/usr/share/bar.py"));

        // drop entries from /usr/share that are not approved ext
        assert!(drop_entry("/usr/share/bar.exe"));

        // unless they are in libexec
        assert!(keep_entry("/usr/share/libexec/bar.exe"));

        // drop entries from /usr/include that are not approved ext
        assert!(drop_entry("/usr/include/bar.h"));

        // todo;; some audit results
        // assert!(drop_entry("/usr/lib64/python3.8/LICENSE.txt"));
        // assert!(drop_entry(
        //     "/usr/share/bash-completion/completions/ctrlaltdel"
        // ));
        // assert!(drop_entry("/usr/share/zoneinfo/right/America/Santa_Isabel"));

        // all others are left in place
        assert!(keep_entry("/foo/bar"));
        assert!(keep_entry("/foo/bar.py"));
    }
}
