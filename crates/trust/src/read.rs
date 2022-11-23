/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use rayon::prelude::*;
use std::collections::HashMap;
use std::path::{Path, PathBuf};

use lmdb::{Cursor, Environment, Transaction};

use crate::db::{Entry, Rec, DB};
use crate::error::Error;
use crate::error::Error::{
    LmdbNotFound, LmdbPermissionDenied, LmdbReadFail, MalformattedTrustEntry, UnsupportedTrustType,
};
use crate::load::TrustSourceEntry;
use crate::source::TrustSource;
use crate::source::TrustSource::{Ancillary, System};
use crate::Trust;

fn relativized_path(i: &(PathBuf, String)) -> (String, &String) {
    (
        // render and split off the filename from full path
        i.0.display()
            .to_string()
            .rsplit_once('/')
            .map(|(_, rhs)| rhs.to_string())
            // if there was no / separator then use the full path
            .unwrap_or_else(|| i.0.display().to_string()),
        &i.1,
    )
}

// pub fn read_rules_d(xs: Vec<TrustSourceEntry>) -> Result<DB, Error> {
//     let lookup: Vec<(String, Entry)> = xs
//         .iter()
//         .map(relativized_path)
//         .map(|(source, l)| (source, parse_trust_record(l)))
//         .flat_map(|(source, r)| match r {
//             Ok((t, rule)) => Some((source, rule)),
//             Ok((_, _)) => None,
//             Err(nom::Err::Error(LineError::CannotParse(i, why))) => {
//                 Some((source, Malformed(i.to_string(), why)))
//             }
//             Err(nom::Err::Error(LineError::CannotParseSet(i, why))) => {
//                 Some((source, MalformedSet(i.to_string(), why)))
//             }
//             Err(_) => None,
//         })
//         .filter_map(|(source, line)| match line {
//             RuleDef(r) => Some((source, Entry::ValidRule(r))),
//             SetDef(s) => Some((source, Entry::ValidSet(s))),
//             Malformed(text, error) => Some((source, Entry::Invalid { text, error })),
//             MalformedSet(text, error) => Some((source, Entry::InvalidSet { text, error })),
//             Comment(text) => Some((source, Entry::Comment(text))),
//             _ => None,
//         })
//         .collect();
//
//     Ok(lint_db(DB::from_sources(lookup)))
// }

pub(crate) fn parse_trust_record(s: &str) -> Result<Trust, Error> {
    let mut v: Vec<&str> = s.rsplitn(3, ' ').collect();
    v.reverse();
    match v.as_slice() {
        [f, sz, sha] => Ok(Trust {
            path: f.to_string(),
            size: sz.parse()?,
            hash: sha.to_string(),
        }),
        _ => Err(MalformattedTrustEntry(s.to_string())),
    }
}

pub fn check_trust_db(db: &DB) -> Result<DB, Error> {
    let lookup: HashMap<String, Rec> = db
        .lookup
        .par_iter()
        .flat_map(|(p, r)| Rec::status_check(r.clone()).map(|r| (p.clone(), r)))
        .collect();

    Ok(DB::from(lookup))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_record() {
        let s =
            "/home/user/my-ls 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87";
        let e = parse_trust_record(s).unwrap();
        assert_eq!(e.path, "/home/user/my-ls");
        assert_eq!(e.size, 157984);
        assert_eq!(
            e.hash,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
        );
    }

    #[test]
    fn parse_record_with_space() {
        let s =
            "/home/user/my ls 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87";
        let e = parse_trust_record(s).unwrap();
        assert_eq!(e.path, "/home/user/my ls");
        assert_eq!(e.size, 157984);
        assert_eq!(
            e.hash,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
        );
    }
}
