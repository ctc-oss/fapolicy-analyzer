/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::db::{Rec, DB};
use crate::error::Error;
use crate::parse;
use rayon::iter::IntoParallelRefIterator;
use std::collections::HashMap;

use rayon::prelude::*;

// 1. checking disk for actual status
pub fn disk_sync(db: &DB) -> Result<DB, Error> {
    let lookup: HashMap<String, Rec> = db
        .lookup
        .par_iter()
        .flat_map(|(p, r)| Rec::status_check(r.clone()).map(|r| (p.clone(), r)))
        .collect();

    Ok(DB::from(lookup))
}

#[derive(Debug)]
pub(crate) struct TrustPair {
    pub k: String,
    pub v: String,
}

impl TrustPair {
    pub(crate) fn new(b: (&[u8], &[u8])) -> TrustPair {
        TrustPair {
            k: String::from_utf8(Vec::from(b.0)).expect("valid utf-8 [k]"),
            v: String::from_utf8(Vec::from(b.1)).expect("valid utf-8 [v]"),
        }
    }
}

type PathRec = (String, Rec);
impl From<TrustPair> for PathRec {
    fn from(kv: TrustPair) -> Self {
        let (tt, v) = kv.v.split_once(' ').expect("value separated by space");
        let (t, s) = parse::strtyped_trust_record(format!("{} {}", kv.k, v).as_str(), tt)
            .unwrap_or_else(|_| panic!("failed to parse string typed trust record: {kv:?}"));
        (t.path.clone(), Rec::from_source(t, s))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::source::TrustSource;
    use assert_matches::assert_matches;

    #[test]
    // todo;; additional coverage for type 2 and invalid type
    fn parse_trust_pair() {
        let tp = TrustPair::new((
            "/home/user/my-ls".as_bytes(),
            "1 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87".as_bytes(),
        ));
        let (_, r) = tp.into();

        assert_eq!(r.trusted.path, "/home/user/my-ls");
        assert_eq!(r.trusted.size, 157984);
        assert_eq!(
            r.trusted.hash,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
        );
        assert_matches!(r.source, Some(TrustSource::System));

        let tp = TrustPair::new((
            "/home/user/my-ls".as_bytes(),
            "2 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87".as_bytes(),
        ));
        let (_, r) = tp.into();
        assert_matches!(r.source, Some(TrustSource::Ancillary))
    }

    fn check_issue1038((_, r): PathRec) {
        assert_eq!(r.trusted.path, "/etc/cron.daily/google-earth-pro");
        assert_eq!(r.trusted.size, 25456);
        assert_eq!(r.trusted.hash, "8c0a49af5a6fc7bd9a0bba09f1e8a6e9");
    }

    // handle sha1 hash entries that contain leading space
    #[test]
    fn issue_1038() {
        // hash leading spaces
        let tp = TrustPair::new((
            "/etc/cron.daily/google-earth-pro".as_bytes(),
            "1 25456                                 8c0a49af5a6fc7bd9a0bba09f1e8a6e9".as_bytes(),
        ));
        check_issue1038(tp.into());

        // hash trailing spaces
        let tp = TrustPair::new((
            "/etc/cron.daily/google-earth-pro".as_bytes(),
            "1 25456                                 8c0a49af5a6fc7bd9a0bba09f1e8a6e9  ".as_bytes(),
        ));
        check_issue1038(tp.into());
    }
}
