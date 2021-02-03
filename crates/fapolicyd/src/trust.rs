use std::fs::File;
use std::io::{prelude::*, BufReader};
use std::str::FromStr;

use api::TrustSource;
use api::TrustSource::Ancillary;

pub fn load_ancillary_trust(path: &str) -> Vec<api::Trust> {
    let f = File::open(path).unwrap();
    let r = BufReader::new(f);

    r.lines()
        .map(|r| r.unwrap())
        .filter(|s| !s.is_empty() && !s.starts_with('#'))
        .map(|l| parse_trust_record(&l).unwrap())
        .collect()
}

// todo;; non-pub
pub fn parse_trust_record(s: &str) -> Result<api::Trust, String> {
    let v: Vec<&str> = s.split(' ').collect();
    match v.as_slice() {
        [f, sz, sha] => Ok(api::Trust {
            path: f.to_string(),
            size: sz.parse().unwrap(),
            hash: Some(sha.to_string()),
            source: TrustSource::Ancillary,
        }),
        _ => Err(String::from("failed to read record")),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn deserialize_entry() {
        let s =
            "/home/user/my-ls 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87";
        let e = parse_trust_record(s).unwrap();
        assert_eq!(e.path, "/home/user/my-ls");
        assert_eq!(e.size, 157984);
        assert_eq!(
            e.hash,
            Some(String::from(
                "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
            ))
        );
    }
}
