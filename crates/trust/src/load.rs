use crate::db::DB;
use crate::error::Error;
use crate::read::{from_dir, from_file, from_lmdb, parse_trust_record};
use crate::Trust;
use std::path::{Path, PathBuf};

use std::process::Command;

use fapolicy_util::rpm::ensure_rpm_exists;
use fapolicy_util::rpm::Error::{ReadRpmDumpFailed, RpmDumpFailed};
use nom::bytes::complete::tag;
use nom::character::complete::alphanumeric1;
use nom::character::complete::digit1;
use nom::character::complete::line_ending;
use nom::character::complete::space1;
use nom::combinator::iterator;
use nom::sequence::{delimited, terminated};
use nom::{InputIter, Parser};

// load all trust files
// load all entries from all files
// write to mutable map with a single entry from each row
//  -- can add diagnostic messages to the entries to flag if they overwrote a dupe
// compare with lmdb, adding diagnostics for anything that is out of sync

pub(crate) type TrustSourceEntry = (PathBuf, String);

/// obtain a [DB]
/// 1. load lmdb records
/// 2. load file trust
/// 3. stir
pub fn trust_db(lmdb: &Path, trust_d: &Path, trust_file: Option<&Path>) -> Result<DB, Error> {
    let mut db = from_lmdb(lmdb)?;
    for (o, t) in file_trust(trust_d, trust_file)? {
        match db.get_mut(&t.path) {
            None => {}
            Some(rec) => {
                rec.origin = Some(o.clone());
            }
        }
    }
    Ok(db)
}

// path to d dir (/etc/fapolicyd/trust.d), optional override file (eg /etc/fapolicyd/fapolicyd.trust
pub fn file_trust(d: &Path, o: Option<&Path>) -> Result<Vec<(String, Trust)>, Error> {
    let mut d_entries = from_dir(d)?;
    let mut o_entries = if let Some(f) = o {
        from_file(f)?
    } else {
        vec![]
    };
    d_entries.append(&mut o_entries);

    Ok(d_entries
        .iter()
        // todo;; support comments elsewhere
        .filter(|(_, txt)| !txt.is_empty() || txt.trim_start().starts_with("#"))
        .map(|(p, txt)| (p.display().to_string(), parse_trust_record(txt.trim())))
        .filter(|(_, r)| r.is_ok())
        .map(|(p, r)| (p, r.unwrap()))
        .collect())
}

/// directly load the rpm database
/// used to analyze the fapolicyd trust db for out of sync issues
pub fn rpm_trust(rpmdb: &Path) -> Result<Vec<Trust>, Error> {
    ensure_rpm_exists()?;

    let args = vec!["-qa", "--dump", "--dbpath", rpmdb.to_str().unwrap()];
    let res = Command::new("rpm")
        .args(args)
        .output()
        .map_err(RpmDumpFailed)?;

    match String::from_utf8(res.stdout) {
        Ok(data) => Ok(parse_rpm_db_entry(&data)),
        Err(_) => Err(ReadRpmDumpFailed.into()),
    }
}

#[derive(Debug)]
struct RpmDbEntry {
    pub path: String,
    pub size: u64,
    pub hash: Option<String>,
}

fn contains_no_files(s: &str) -> nom::IResult<&str, Option<RpmDbEntry>> {
    delimited(tag("("), tag("contains no files"), tag(")"))(s).map(|x| (x.0, None))
}

fn parse_rpm_db_entry(s: &str) -> Vec<Trust> {
    iterator(s, terminated(contains_no_files.or(parse_line), line_ending))
        .collect::<Vec<Option<RpmDbEntry>>>()
        .iter()
        .flatten()
        .filter(|e| keep_entry(&e.path))
        .flat_map(|e| {
            e.hash.as_ref().map(|hash| Trust {
                path: e.path.clone(),
                size: e.size,
                hash: hash.clone(),
            })
        })
        .collect()
}

fn filepath(i: &str) -> nom::IResult<&str, &str> {
    nom::bytes::complete::is_not(" \t\n")(i)
}

fn modestring(i: &str) -> nom::IResult<&str, &str> {
    nom::bytes::complete::is_a("01234567")(i)
}

fn digest_or_not(i: &str) -> Option<&str> {
    if i.iter_elements().all(|c| c == '0') {
        None
    } else {
        Some(i)
    }
}

fn int_to_bool(i: &str) -> bool {
    match i {
        "0" => false,
        "1" => true,
        v => panic!("invalid bool value {}", v),
    }
}

fn is_dir(mode: &str) -> bool {
    mode.starts_with("040")
}

/// path size mtime digest mode owner group isconfig isdoc rdev symlink
fn parse_line(i: &str) -> nom::IResult<&str, Option<RpmDbEntry>> {
    match nom::combinator::complete(nom::sequence::tuple((
        terminated(filepath, space1),
        terminated(digit1, space1),
        terminated(digit1, space1),
        terminated(alphanumeric1, space1),
        terminated(modestring, space1),
        terminated(alphanumeric1, space1),
        terminated(alphanumeric1, space1),
        terminated(digit1, space1).map(int_to_bool),
        terminated(digit1, space1).map(int_to_bool),
        terminated(digit1, space1),
        filepath,
    )))(i)
    {
        Ok((
            remaining_input,
            (
                path,
                size,
                _, // mtime
                digest,
                mode,
                _, // owner
                _, // group
                is_cfg,
                is_doc,
                _, // rdev
                _, // symlink
            ),
        )) if !is_cfg && !is_doc && !is_dir(mode) => Ok((
            remaining_input,
            Some(RpmDbEntry {
                path: path.to_string(),
                size: size.parse().unwrap(),
                hash: digest_or_not(digest).map(|s| s.to_string()),
            }),
        )),
        Ok((remaining_input, _)) => Ok((remaining_input, None)),
        Err(e) => Err(e),
    }
}

const USR_SHARE_ALLOWED_EXTS: [&str; 15] = [
    "pyc", "pyo", "py", "rb", "pl", "stp", "js", "jar", "m4", "php", "el", "pm", "lua", "class",
    "elc",
];

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

//////////

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn with_contains_no_files_lines() {
        let full = format!(
            "{}\n,{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n",
            NF, A, NF, B, NF, C, NF, D, NF
        );
        let r = parse_rpm_db_entry(&full);
        assert_eq!(2, r.len());
    }

    static NF: &str = "(contains no files)";
    static A: &str = "/usr/bin/hostname 21664 1557584275 26532eeae676157e70231d911474e48d31085b5f2e511ce908349dbb02f0f69c 0100755 root root 0 0 0 X";
    static B: &str = "/usr/share/man/man1/dnsdomainname.1.gz 13 1557584275 0000000000000000000000000000000000000000000000000000000000000000 0120777 root root 0 1 0 hostname.1.gz";
    static C: &str = "/usr/lib/.build-id/a8/a7ee9d5002492edfc62e3e2e44149e981f9866 28 1557584275 0000000000000000000000000000000000000000000000000000000000000000 0120777 root root 0 0 0 ../../../../usr/bin/hostname";
    static D: &str = "/usr/bin/tar 459928 1595282074 7642954ec2d8cd43ac345eca0b4a20fc5d44811a309e62fa78340cce8cff10cc 0100755 root root 0 0 0 X";

    #[test]
    fn parse_a() {
        let expected = RpmDbEntry {
            path: "/usr/bin/hostname".to_string(),
            size: 21664,
            hash: Some(
                "26532eeae676157e70231d911474e48d31085b5f2e511ce908349dbb02f0f69c".to_string(),
            ),
        };
        let (_, actual) = parse_line(A).unwrap();

        let e = actual.as_ref().unwrap();
        assert_eq!(e.path, expected.path);
        assert_eq!(e.size, expected.size);
        assert_eq!(e.hash, expected.hash);
    }

    #[test]
    fn parse_b() {
        // b is doc, filtered out
        let (_, actual) = parse_line(B).unwrap();
        assert!(actual.is_none());
    }

    #[test]
    fn parse_c() {
        let expected = RpmDbEntry {
            path: "/usr/lib/.build-id/a8/a7ee9d5002492edfc62e3e2e44149e981f9866".to_string(),
            size: 28,
            hash: None,
        };
        let (_, actual) = parse_line(C).unwrap();

        let e = actual.as_ref().unwrap();
        assert_eq!(e.path, expected.path);
        assert_eq!(e.size, expected.size);
        assert_eq!(e.hash, expected.hash);
    }

    #[test]
    fn parse_db() {
        let abc = format!("{}\n{}\n{}\n{}\n", A, B, C, D);
        let files: Vec<Trust> = parse_rpm_db_entry(&abc);
        assert_eq!(files.len(), 2);
    }

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
        // assert!(drop_entry("/usr/lib64/python3.6/LICENSE.txt"));
        // assert!(drop_entry(
        //     "/usr/share/bash-completion/completions/ctrlaltdel"
        // ));
        // assert!(drop_entry("/usr/share/zoneinfo/right/America/Santa_Isabel"));

        // all others are left in place
        assert!(keep_entry("/foo/bar"));
        assert!(keep_entry("/foo/bar.py"));
    }
}
