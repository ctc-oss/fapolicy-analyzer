use crate::api;
use crate::rpm::RpmError::{Discovery, Execution, NotFound};
use nom::character::complete::alphanumeric1;
use nom::character::complete::digit1;
use nom::character::complete::line_ending;
use nom::character::complete::space1;
use nom::combinator::iterator;
use nom::sequence::terminated;
use nom::InputIter;
use std::process::Command;

pub fn load_system_trust(rpmdb: &Option<String>) -> Vec<api::Trust> {
    let mut args = Vec::new();
    args.push("-qa");
    args.push("--dump");

    // todo;; for now we are always setting this to support ubuntu dev environments
    args.push("--dbpath");
    if let Some(rpmdb_path) = rpmdb {
        args.push(rpmdb_path);
    } else {
        args.push("/var/lib/rpm")
    }

    let res = Command::new("rpm")
        .args(args)
        .output()
        .expect("failed to execute process");

    let clean = String::from_utf8(res.stdout).unwrap();
    parse(&clean)
}

fn parse(s: &str) -> Vec<api::Trust> {
    iterator(s, terminated(parse_line, line_ending)).collect()
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

/// path size mtime digest mode owner group isconfig isdoc rdev symlink
pub fn parse_line(i: &str) -> nom::IResult<&str, api::Trust> {
    match nom::combinator::complete(nom::sequence::tuple((
        filepath,
        space1,
        digit1,
        space1,
        digit1,
        space1,
        alphanumeric1,
        space1,
        modestring,
        space1,
        alphanumeric1,
        space1,
        alphanumeric1,
        space1,
        digit1,
        space1,
        digit1,
        space1,
        digit1,
        space1,
        filepath,
    )))(i)
    {
        Ok((
            remaining_input,
            (
                path,
                _,
                size,
                _,
                _,
                _, // mtime
                digest,
                _,
                _,
                _, // mode
                _,
                _, // owner
                _,
                _, // group
                _,
                _, // isconfig
                _,
                _, // isdoc
                _,
                _, // rdev
                _, // symlink
            ),
        )) => Ok((
            remaining_input,
            api::Trust {
                path: path.to_string(),
                size: size.parse().unwrap(),
                hash: digest_or_not(digest).map(|s| s.to_string()),
                source: api::TrustSource::System,
            },
        )),
        Err(e) => Err(e),
    }
}

//////////

#[cfg(test)]
mod tests {
    use super::*;

    static A: &str = "/usr/bin/hostname 21664 1557584275 26532eeae676157e70231d911474e48d31085b5f2e511ce908349dbb02f0f69c 0100755 root root 0 0 0 X";
    static B: &str = "/usr/share/man/man1/dnsdomainname.1.gz 13 1557584275 0000000000000000000000000000000000000000000000000000000000000000 0120777 root root 0 1 0 hostname.1.gz";
    static C: &str = "/usr/lib/.build-id/a8/a7ee9d5002492edfc62e3e2e44149e981f9866 28 1557584275 0000000000000000000000000000000000000000000000000000000000000000 0120777 root root 0 0 0 ../../../../usr/bin/hostname";

    #[test]
    fn parse_a() {
        let expected = api::Trust {
            path: "/usr/bin/hostname".to_string(),
            size: 21664,
            hash: Some(
                "26532eeae676157e70231d911474e48d31085b5f2e511ce908349dbb02f0f69c".to_string(),
            ),
            source: api::TrustSource::System,
        };
        let (_, actual) = parse_line(A).unwrap();
        println!("{:?}", actual);

        assert_eq!(actual.path, expected.path);
        assert_eq!(actual.size, expected.size);
        assert_eq!(actual.hash, expected.hash);
    }

    #[test]
    fn parse_b() {
        let expected = api::Trust {
            path: "/usr/share/man/man1/dnsdomainname.1.gz".to_string(),
            size: 13,
            hash: None,
            source: api::TrustSource::System,
        };
        let (_, actual) = parse_line(B).unwrap();
        println!("{:?}", actual);

        assert_eq!(actual.path, expected.path);
        assert_eq!(actual.size, expected.size);
        assert_eq!(actual.hash, expected.hash);
    }

    #[test]
    fn parse_c() {
        let expected = api::Trust {
            path: "/usr/lib/.build-id/a8/a7ee9d5002492edfc62e3e2e44149e981f9866".to_string(),
            size: 28,
            hash: None,
            source: api::TrustSource::System,
        };
        let (_, actual) = parse_line(C).unwrap();
        println!("{:?}", actual);

        assert_eq!(actual.path, expected.path);
        assert_eq!(actual.size, expected.size);
        assert_eq!(actual.hash, expected.hash);
    }

    #[test]
    fn parse_db() {
        let mut abc = String::new();
        abc.push_str(A);
        abc.push('\n');
        abc.push_str(B);
        abc.push('\n');
        abc.push_str(C);
        abc.push('\n');

        let files: Vec<api::Trust> = parse(&abc);

        assert_eq!(files.len(), 3);
        for x in files {
            println!("{:?}", x);
        }
    }
}

#[derive(Debug, Clone)]
pub enum RpmError {
    Discovery,
    NotFound,
    Execution,
}

// return rpm version
pub fn check_rpm() -> Result<String, RpmError> {
    match Command::new("which").arg("rpm").output() {
        Ok(eo) if eo.status.success() => {
            let rpmpath = String::from_utf8(eo.stdout).unwrap().trim().to_string();
            match Command::new(&rpmpath).arg("--version").output() {
                Ok(vo) if vo.status.success() => {
                    let rpmver = String::from_utf8(vo.stdout).unwrap().trim().to_string();
                    Ok(rpmver)
                }
                _ => Err(Execution),
            }
        }
        Ok(_) => Err(NotFound),
        _ => Err(Discovery),
    }
}
