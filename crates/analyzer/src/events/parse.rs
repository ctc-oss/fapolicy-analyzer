/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use nom::bytes::complete::{tag, take_until};
use nom::character::complete::space0;
use nom::character::complete::{digit1, space1};
use nom::multi::separated_list1;
use nom::sequence::{preceded, terminated};

use crate::events::event::Event;
use fapolicy_rules::*;

pub fn parse_event(i: &str) -> nom::IResult<&str, Event> {
    match nom::combinator::complete(nom::sequence::tuple((
        take_until("rule="),
        terminated(preceded(tag("rule="), digit1), space1),
        terminated(preceded(tag("dec="), parse::decision), space1),
        terminated(parse::permission, space1),
        terminated(preceded(tag("uid="), digit1), space1),
        terminated(
            preceded(tag("gid="), separated_list1(tag(","), digit1)),
            space1,
        ),
        terminated(preceded(tag("pid="), digit1), space1),
        terminated(parse::subject, space1),
        terminated(tag(":"), space0),
        parse::object,
    )))(i)
    {
        Ok((remaining_input, (_, id, dec, perm, uid, gid, pid, subj, _, obj))) => Ok((
            remaining_input,
            Event {
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

#[cfg(test)]
mod tests {
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
}
