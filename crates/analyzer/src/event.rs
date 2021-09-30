use std::fmt::Display;
use std::fs::File;
use std::io::{prelude::*, BufReader};
use std::iter::Iterator;
use std::str::FromStr;

use fapolicy_trust::db::DB as TrustDB;

use crate::error::Error;
use crate::error::Error::AnalyzerError;
use crate::log::parse_event;
use crate::rules::db::DB as RulesDB;
use crate::rules::Decision::*;
use crate::rules::*;

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

impl Event {
    pub fn from_file(path: &str) -> Vec<Event> {
        let f = File::open(path).unwrap();
        let r = BufReader::new(f);

        r.lines()
            .map(|r| r.unwrap())
            .filter(|s| !s.is_empty() && !s.starts_with('#'))
            .map(|l| parse_event(&l).unwrap().1)
            .collect()
    }
}

fn trust_check(path: &str, db: &TrustDB) -> Result<String, Error> {
    match db.get(path) {
        Some(r) if r.is_system() => Ok("ST".into()),
        Some(r) if r.is_ancillary() => Ok("AT".into()),
        None => Ok("U".into()),
        _ => Err(AnalyzerError("unexpected trust check state".into())),
    }
}

fn any_denials_for_subject(p: &str, events: &Vec<Event>) -> bool {
    events
        .iter()
        .filter(|e| match e.subj.exe() {
            Some(exe) if &exe == p => true,
            _ => false,
        })
        .find(|e| match e.dec {
            Deny | DenyLog | DenySyslog | DenyAudit => true,
            _ => false,
        })
        .is_some()
}

fn any_allows_for_subject(p: &str, events: &Vec<Event>) -> bool {
    events
        .iter()
        .filter(|e| match e.subj.exe() {
            Some(exe) if &exe == p => true,
            _ => false,
        })
        .find(|e| match e.dec {
            Allow | AllowLog | AllowSyslog | AllowAudit => true,
            _ => false,
        })
        .is_some()
}

pub fn analyze(events: Vec<Event>, trust: &TrustDB, _: &RulesDB) -> Vec<Analysis> {
    events
        .iter()
        .map(|e| {
            let sp = e.subj.exe().unwrap();
            let op = e.obj.path().unwrap();

            let ed = match e.dec {
                Allow | AllowLog | AllowSyslog | AllowAudit => "A".to_string(),
                Deny | DenyLog | DenySyslog | DenyAudit => "D".to_string(),
            };

            let sa = match (
                any_allows_for_subject(&sp, &events),
                any_denials_for_subject(&sp, &events),
            ) {
                (true, false) => "A".to_string(),
                (false, true) => "D".to_string(),
                _ => "P".to_string(),
            };

            Analysis {
                event: e.clone(),
                subject: SubjAnalysis {
                    trust: trust_check(&sp, trust).unwrap(),
                    access: sa,
                    file: sp,
                },
                object: ObjAnalysis {
                    trust: trust_check(&op, trust).unwrap(),
                    access: ed,
                    mode: "R".to_string(),
                    file: op,
                },
            }
        })
        .collect()
}

#[derive(Clone, Debug)]
pub struct Analysis {
    pub event: Event,
    pub subject: SubjAnalysis,
    pub object: ObjAnalysis,
}

#[derive(Clone, Debug)]
pub struct SubjAnalysis {
    pub file: String,
    pub trust: String,
    pub access: String,
}

#[derive(Clone, Debug)]
pub struct ObjAnalysis {
    pub file: String,
    pub trust: String,
    pub access: String,
    pub mode: String,
}
