use crate::fapolicyd;
use crate::version::Error::MalformedVersionString;
use thiserror::Error;

use fapolicy_util::rpm;
use nom::bytes::complete::tag;
use nom::character::complete::digit1;
use nom::combinator::opt;
use nom::sequence::{preceded, terminated};
use nom::IResult;

#[derive(Error, Debug)]
pub enum Error {
    #[error("Error reading trust from RPM DB {0}")]
    RpmError(#[from] rpm::Error),
    #[error("could not parse version string {0}")]
    MalformedVersionString(String),
}

pub fn fapolicyd_version() -> fapolicyd::Version {
    match rpm_q_fapolicyd() {
        Ok(v) => v,
        Err(e) => {
            eprintln!("Unable to detect fapolicyd version: {:?}", e);
            fapolicyd::Version::Unknown
        }
    }
}

fn rpm_q_fapolicyd() -> Result<fapolicyd::Version, Error> {
    let (_, v) = rpm::rpm_q("fapolicyd")?;
    match parse_semver(&v) {
        Ok((_, (major, minor, patch))) => Ok(fapolicyd::Version::Release {
            major,
            minor,
            patch,
        }),
        Err(_) => Err(MalformedVersionString(v)),
    }
}

// fapolicyd has been observed to have two and three part version numbers
// the parser is constructed to allow the third part to be optional, defaulting to 0
fn parse_semver(i: &str) -> IResult<&str, (u8, u8, u8)> {
    nom::combinator::complete(nom::sequence::tuple((
        terminated(digit1, tag(".")),
        digit1,
        opt(preceded(tag("."), digit1)),
    )))(i)
    .map(|(r, (major, minor, patch))| {
        (
            r,
            (
                major.parse::<u8>().unwrap(),
                minor.parse::<u8>().unwrap(),
                patch.unwrap_or("0").parse::<u8>().unwrap(),
            ),
        )
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_semver() -> Result<(), Box<dyn std::error::Error>> {
        // 2
        let v = "1.1";
        assert_eq!((1, 1, 0), parse_semver(v)?.1);

        let v = "0.0";
        assert_eq!((0, 0, 0), parse_semver(v)?.1);

        let v = "0.99";
        assert_eq!((0, 99, 0), parse_semver(v)?.1);

        // 3
        let v = "1.0.3";
        assert_eq!((1, 0, 3), parse_semver(v)?.1);

        let v = "11.0.3";
        assert_eq!((11, 0, 3), parse_semver(v)?.1);

        let v = "0.9.3";
        assert_eq!((0, 9, 3), parse_semver(v)?.1);

        Ok(())
    }
}
