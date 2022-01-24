/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fmt::Display;
use std::iter::Iterator;
use std::str::FromStr;

use chrono::{DateTime, Utc};

use fapolicy_rules::*;

use crate::events::parse::parse_event;

#[derive(Clone, Debug, PartialEq)]
pub struct Event {
    pub rule_id: i32,
    pub dec: Decision,
    pub perm: Permission,
    pub uid: i32,
    pub gid: Vec<i32>,
    pub pid: i32,
    pub subj: Subject,
    pub obj: Object,
    pub when: Option<DateTime<Utc>>,
}

impl FromStr for Event {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match parse_event(s) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Event from string".into()),
        }
    }
}

impl Display for Event {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_fmt(format_args!("rule={} ", self.rule_id))?;
        f.write_fmt(format_args!("dec={} ", self.dec))?;
        f.write_fmt(format_args!("{} ", self.perm))?;
        f.write_fmt(format_args!("uid={} ", self.uid))?;
        f.write_fmt(format_args!(
            "gid={} ",
            self.gid
                .iter()
                .map(|v| format!("{}", v))
                .collect::<Vec<String>>()
                .join(",")
        ))?;
        f.write_fmt(format_args!("pid={} ", self.pid))?;
        f.write_fmt(format_args!("exe={} ", self.subj.exe().unwrap()))?;
        f.write_str(": ")?;
        let o = self
            .obj
            .parts
            .iter()
            .fold(String::new(), |x, p| format!("{} {}", x, p));
        f.write_fmt(format_args!("{} ", o))?;

        Ok(())
    }
}

#[derive(Clone)]
pub enum Perspective {
    User(i32),
    Group(i32),
    Subject(String),
}

impl Perspective {
    pub fn fit(&self, e: &Event) -> bool {
        match self {
            Perspective::User(uid) => *uid == e.uid,
            Perspective::Group(gid) => e.gid.contains(gid),
            Perspective::Subject(subj) => &e.subj.exe().unwrap() == subj,
        }
    }
}
