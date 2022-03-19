/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use chrono::{DateTime, NaiveDate, NaiveDateTime, NaiveTime, Utc};
use nom::branch::alt;
use nom::bytes::complete::{tag, take_until};
use nom::character::complete::anychar;
use nom::character::complete::{digit1, space1};
use nom::combinator::opt;
use nom::multi::separated_list1;
use nom::sequence::{preceded, separated_pair, terminated};

use fapolicy_rules::*;

use crate::events::event::Event;

pub fn parse_event(i: &str) -> nom::IResult<&str, Event> {
    match nom::combinator::complete(nom::sequence::tuple((
        opt(rfc3339_date),
        take_until("rule="),
        terminated(preceded(tag("rule="), digit1), space1),
        terminated(preceded(tag("dec="), parser::legacy::decision), space1),
        terminated(parser::legacy::permission, space1),
        terminated(preceded(tag("uid="), digit1), space1),
        terminated(
            preceded(tag("gid="), separated_list1(tag(","), digit1)),
            space1,
        ),
        terminated(preceded(tag("pid="), digit1), space1),
        parser::legacy::subject,
        // note;; the separator is processed by the subject and object parsers internally since v2
        // terminated(tag(":"), space0),
        parser::legacy::object,
    )))(i)
    {
        Ok((remaining_input, (when, _, id, dec, perm, uid, gid, pid, subj, obj))) => Ok((
            remaining_input,
            Event {
                when,
                rule_id: id.parse().unwrap(),
                dec,
                perm,
                uid: uid.parse().unwrap(),
                gid: gid.iter().map(|s| s.parse().unwrap()).collect(),
                pid: pid.parse().unwrap(),
                subj,
                obj,
            },
        )),
        Err(e) => Err(e),
    }
}

fn rfc3339_date(i: &str) -> nom::IResult<&str, DateTime<Utc>> {
    match nom::combinator::complete(nom::sequence::tuple((
        terminated(digit1, tag("-")), // y
        terminated(digit1, tag("-")), // m
        digit1,                       // d
        anychar,
        terminated(digit1, tag(":")),             // h
        terminated(digit1, tag(":")),             // m
        terminated(digit1, tag(".")),             // s
        digit1,                                   // ns
        alt((tag("+"), tag("-"))),                // offset +,-
        separated_pair(digit1, tag(":"), digit1), // offset
    )))(i)
    {
        Ok((remaining_input, (y, m, d, _, h, min, s, _, _, (_, _)))) => Ok((
            remaining_input,
            DateTime::from_utc(
                NaiveDateTime::new(
                    NaiveDate::from_ymd(y.parse().unwrap(), m.parse().unwrap(), d.parse().unwrap()),
                    NaiveTime::from_hms(
                        h.parse().unwrap(),
                        min.parse().unwrap(),
                        s.parse().unwrap(),
                    ),
                ),
                Utc,
            ),
        )),
        Err(e) => Err(e),
    }
}

#[cfg(test)]
mod tests {
    use chrono::{Datelike, Timelike};

    use super::*;

    #[test]
    fn simple() {
        let e = "rule=9 dec=allow perm=execute uid=1003 gid=999 pid=5555 exe=/usr/bin/bash : path=/usr/bin/vi ftype=application/x-executable";
        let (rem, e) = parse_event(e).ok().unwrap();
        assert_eq!(9, e.rule_id);
        assert!(rem.is_empty());
        assert_eq!(e.dec, Decision::Allow);
        assert_eq!(e.perm, Permission::Execute);
        assert_eq!(e.uid, 1003);
        assert_eq!(e.gid, vec![999]);
        assert_eq!(e.pid, 5555);
    }

    #[test]
    fn multi_gid() {
        let e = "rule=9 dec=allow perm=execute uid=1003 gid=123,456,789 pid=5555 exe=/usr/bin/bash : path=/usr/bin/vi ftype=application/x-executable";
        let (rem, e) = parse_event(e).ok().unwrap();
        assert!(rem.is_empty());
        assert_eq!(e.gid, vec![123, 456, 789]);
    }

    #[test]
    fn timestamped() {
        let e = "2021-12-28T11:59:09.388568+00:00 fedora fapolicyd[17294]: rule=3 dec=allow_syslog perm=execute uid=1004 gid=100,1002 pid=50519 exe=/usr/bin/bash : path=/usr/lib64/ld-2.33.so ftype=application/x-sharedlib trust=1";
        let (rem, e) = parse_event(e).ok().unwrap();
        assert!(rem.is_empty());
        assert_eq!(e.gid, vec![100, 1002]);

        let t = e.when.unwrap();
        assert_eq!(t.date().year(), 2021);
        assert_eq!(t.date().month(), 12);
        assert_eq!(t.date().day(), 28);
        assert_eq!(t.time().hour(), 11);
        assert_eq!(t.time().minute(), 59);
        assert_eq!(t.time().second(), 9);
    }

    #[test]
    fn rfc3339_timestamp() {
        let t = rfc3339_date("2021-12-28T11:59:09.388568+00:00");
        assert!(t.is_ok());

        let (_, t) = t.ok().unwrap();
        assert_eq!(t.date().year(), 2021);
        assert_eq!(t.date().month(), 12);
        assert_eq!(t.date().day(), 28);
        assert_eq!(t.time().hour(), 11);
        assert_eq!(t.time().minute(), 59);
        assert_eq!(t.time().second(), 9);
    }
}
