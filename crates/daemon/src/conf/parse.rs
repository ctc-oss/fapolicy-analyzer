use nom::branch::alt;
use nom::bytes::complete::tag;
use nom::character::complete::{alphanumeric1, digit1};
use nom::multi::separated_list0;
use nom::IResult;

use crate::conf::config::{ConfigToken, IntegritySource, TrustBackend};
use crate::conf::error::Error;
use crate::conf::error::Error::{
    ExpectedBool, ExpectedIntegritySource, ExpectedNumber, ExpectedString, ExpectedStringList,
    General, Unexpected, UnknownTrustBackend,
};

fn parse_bool(i: &str) -> Result<bool, Error> {
    match nom_num(i) {
        Ok(("", v)) if v == 1 => Ok(true),
        Ok(("", v)) if v == 0 => Ok(false),
        Ok((_, _)) => Err(Unexpected(i.to_string())),
        Err(_) => Err(General),
    }
}

fn parse_number(i: &str) -> Result<usize, Error> {
    match nom_num(i) {
        Ok(("", v)) => Ok(v),
        Ok((_, _)) => Err(Unexpected(i.to_string())),
        Err(_) => Err(General),
    }
}

fn nom_str(i: &str) -> IResult<&str, &str> {
    alphanumeric1(i)
}

fn nom_num(i: &str) -> IResult<&str, usize, Error> {
    digit1(i).map(|(r, v)| (r, v.parse().unwrap()))
}

fn parse_string(i: &str) -> Result<String, Error> {
    match nom_str(i) {
        Ok(("", v)) => v.parse().map_err(|_| ExpectedString),
        Ok((_, _)) => Err(Unexpected(i.to_string())),
        Err(_) => Err(General),
    }
}

fn parse_trust_backend(i: &str) -> Result<Vec<TrustBackend>, Error> {
    use TrustBackend::*;

    let mut res = vec![];
    for s in parse_string_list(i)? {
        match s.as_str() {
            "rpmdb" => res.push(Rpm),
            "file" => res.push(File),
            "deb" => res.push(Deb),
            unk => return Err(UnknownTrustBackend(unk.to_string())),
        }
    }
    Ok(res)
}

fn parse_integrity(i: &str) -> Result<IntegritySource, Error> {
    match parse_string(i.trim()).as_deref() {
        Ok("none") => Ok(IntegritySource::None),
        Ok("hash") => Ok(IntegritySource::Hash),
        Ok("size") => Ok(IntegritySource::Size),
        Ok(_) => Err(ExpectedIntegritySource),
        Err(e) => Err(e.clone()),
    }
}

fn parse_syslog_format(i: &str) -> Result<Vec<String>, Error> {
    match nom_syslog_list(i) {
        Ok(("", l)) => Ok(l.into_iter().map(|s| s.to_string()).collect()),
        Ok((_, _)) => Err(Unexpected(i.to_string())),
        Err(_) => Err(General),
    }
}

fn parse_string_list(i: &str) -> Result<Vec<String>, Error> {
    match nom_str_list(i) {
        Ok(("", l)) => Ok(l.into_iter().map(|s| s.to_string()).collect()),
        Ok((_, _)) => Err(Unexpected(i.to_string())),
        Err(_) => Err(General),
    }
}

fn nom_str_list(i: &str) -> IResult<&str, Vec<&str>> {
    separated_list0(tag(","), nom_str)(i)
}

fn nom_syslog_list(i: &str) -> IResult<&str, Vec<&str>> {
    separated_list0(tag(","), alt((nom_str, tag(":"))))(i)
}

pub(crate) fn token(i: &str) -> Result<ConfigToken, (&str, &str, Error)> {
    use ConfigToken::*;
    match i.split_once("=") {
        None | Some(("", _)) => Err(("", "", Error::MalformedConfig)),
        Some((lhs, rhs)) => {
            let rhs = rhs.trim();
            match lhs.trim() {
                // bools
                "permissive" => parse_bool(rhs)
                    .map(Permissive)
                    .map_err(|_| (lhs, rhs, ExpectedBool)),
                "do_stat_report" => parse_bool(rhs)
                    .map(DoStatReport)
                    .map_err(|_| (lhs, rhs, ExpectedBool)),
                "detailed_report" => parse_bool(rhs)
                    .map(DetailedReport)
                    .map_err(|_| (lhs, rhs, ExpectedBool)),
                "rpm_sha256_only" => parse_bool(rhs)
                    .map(RpmSha256Only)
                    .map_err(|_| (lhs, rhs, ExpectedBool)),
                "allow_filesystem_mark" => parse_bool(rhs)
                    .map(AllowFsMark)
                    .map_err(|_| (lhs, rhs, ExpectedBool)),
                // numbers
                "nice_val" => parse_number(rhs)
                    .map(NiceVal)
                    .map_err(|_| (lhs, rhs, ExpectedNumber)),
                "q_size" => parse_number(rhs)
                    .map(QSize)
                    .map_err(|_| (lhs, rhs, ExpectedNumber)),
                "db_max_size" => parse_number(rhs)
                    .map(DbMaxSize)
                    .map_err(|_| (lhs, rhs, ExpectedNumber)),
                "subj_cache_size" => parse_number(rhs)
                    .map(SubjCacheSize)
                    .map_err(|_| (lhs, rhs, ExpectedNumber)),
                "obj_cache_size" => parse_number(rhs)
                    .map(ObjCacheSize)
                    .map_err(|_| (lhs, rhs, ExpectedNumber)),
                // strings
                "watch_fs" => parse_string_list(rhs)
                    .map(WatchFs)
                    .map_err(|_| (lhs, rhs, ExpectedStringList)),
                "syslog_format" => parse_syslog_format(rhs)
                    .map(SyslogFormat)
                    .map_err(|_| (lhs, rhs, ExpectedStringList)),
                "uid" => parse_string(rhs)
                    .map(UID)
                    .map_err(|_| (lhs, rhs, ExpectedString)),
                "gid" => parse_string(rhs)
                    .map(GID)
                    .map_err(|_| (lhs, rhs, ExpectedString)),
                // typed
                "trust" => parse_trust_backend(rhs)
                    .map(Trust)
                    .map_err(|e| (lhs, rhs, e)),
                "integrity" => parse_integrity(rhs)
                    .map(Integrity)
                    .map_err(|e| (lhs, rhs, e)),
                unsupported => Err((unsupported, rhs, Error::InvalidLhs(unsupported.to_string()))),
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use assert_matches::assert_matches;

    use crate::conf::config::ConfigToken::*;
    use crate::conf::error::Error;
    use crate::conf::parse::{parse_bool, token};

    #[test]
    fn test_parse_bool() {
        assert_matches!(parse_bool("0"), Ok(false));
        assert_matches!(parse_bool("1"), Ok(true));
        assert_matches!(parse_bool("2"), Err(_));
        assert_matches!(parse_bool("x"), Err(_));
        assert_matches!(parse_bool(""), Err(_));
    }

    #[test]
    fn test_p2_malformed_config() {
        assert_matches!(token(""), Err(Error::MalformedConfig));
        assert_matches!(token("foo"), Err(Error::MalformedConfig));
        assert_matches!(token("foo="), Err(Error::MalformedConfig));
        assert_matches!(token("=foo"), Err(Error::MalformedConfig));
    }

    #[test]
    fn test_p2_permissive() {
        assert_matches!(token("permissive=0"), Ok(Permissive(false)));
        assert_matches!(token("permissive=1"), Ok(Permissive(true)));
        assert_matches!(token("permissive=foo"), Err(Error::ExpectedBool));
    }

    #[test]
    fn test_p2_nice_val() {
        assert_matches!(token("nice_val="), Err(Error::MalformedConfig));
        assert_matches!(token("nice_val=0"), Ok(NiceVal(0)));
        assert_matches!(token("nice_val=14"), Ok(NiceVal(14)));
        assert_matches!(token("nice_val=foo"), Err(Error::ExpectedNumber));
    }

    #[test]
    fn test_p2_watch_fs() {
        // assert_matches!(p2("watch_fs="), Ok(WatchFs(v)) if v.is_empty());
        assert_matches!(token("watch_fs=ext2"), Ok(WatchFs(v)) if v.len() == 1);
        assert_matches!(
            token("watch_fs=ext2,ext3"),
            Ok(WatchFs(v)) if v.len() == 2
        );
    }

    #[test]
    fn test_p2_trust_sources() {
        // assert_matches!(p2("trust="), Ok(Trust(v)) if v.is_empty());
        assert_matches!(token("trust=rpm"), Ok(Trust(v)) if v.len() == 1);
        assert_matches!(token("trust=rpm,file"), Ok(Trust(v)) if v.len() == 2);
    }
}
