/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use fapolicy_trust::db::DB as TrustDB;
use std::collections::hash_map::Entry;
use std::collections::HashMap;

use crate::error::Error;
use crate::error::Error::AnalyzerError;
use crate::events::db::DB as EventDB;
use crate::events::event::{Event, Perspective};
use fapolicy_rules::Decision::*;
use fapolicy_rules::Permission;
use fapolicy_trust::stat::Status::{Discrepancy, Missing, Trusted};

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
    pub status: String,
    pub access: String,
}

#[derive(Clone, Debug)]
pub struct ObjAnalysis {
    pub file: String,
    pub trust: String,
    pub status: String,
    pub access: String,
    pub perm: String,
}

pub fn analyze(db: &EventDB, from: Perspective, trust: &TrustDB) -> Vec<Analysis> {
    let fit_events: Vec<Event> = db.events.iter().filter(|&e| from.fit(e)).cloned().collect();
    let mut access_map: HashMap<String, String> = HashMap::new();

    fit_events
        .iter()
        .map(|e| {
            let sp = e.subj.exe().unwrap();
            let op = e.obj.path().unwrap();

            let ed = match e.dec {
                Allow | AllowLog | AllowSyslog | AllowAudit => "A".to_string(),
                Deny | DenyLog | DenySyslog | DenyAudit => "D".to_string(),
            };

            let sa = match access_map.entry(sp.clone()) {
                Entry::Occupied(e) => e.get().clone(),
                Entry::Vacant(e) => {
                    let sa = match (
                        any_allows_for_subject(&sp, &fit_events),
                        any_denials_for_subject(&sp, &fit_events),
                    ) {
                        (true, false) => "A".to_string(),
                        (false, true) => "D".to_string(),
                        _ => "P".to_string(),
                    };
                    e.insert(sa.clone());
                    sa
                }
            };

            Analysis {
                event: e.clone(),
                subject: SubjAnalysis {
                    trust: trust_source(&sp, trust).unwrap(),
                    status: trust_status(&sp, trust).unwrap(),
                    access: sa,
                    file: sp,
                },
                object: ObjAnalysis {
                    trust: trust_source(&op, trust).unwrap(),
                    status: trust_status(&op, trust).unwrap(),
                    access: ed,
                    perm: perm_to_display(&e.perm),
                    file: op,
                },
            }
        })
        .collect()
}

const PERM_SPLIT: usize = "perm=".len();
fn perm_to_display(p: &Permission) -> String {
    p.to_string().split_at(PERM_SPLIT).1.to_string()
}

fn trust_source(path: &str, db: &TrustDB) -> Result<String, Error> {
    match db.get(path) {
        Some(r) if r.is_system() => Ok("ST".into()),
        Some(r) if r.is_ancillary() => Ok("AT".into()),
        None => Ok("U".into()),
        _ => Err(AnalyzerError("unexpected trust check state".into())),
    }
}

fn trust_status(path: &str, db: &TrustDB) -> Result<String, Error> {
    match db.get(path) {
        Some(r) if r.status.as_ref().is_some() => match r.status.as_ref().unwrap() {
            Trusted(_, _) => Ok("T".into()),
            Discrepancy(_, _) => Ok("D".into()),
            Missing(_) => Ok("U".into()),
        },
        _ => Ok("U".into()),
    }
}

fn any_denials_for_subject(p: &str, events: &[Event]) -> bool {
    events
        .iter()
        .filter(|e| matches!( e.subj.exe(), Some(exe) if exe == p))
        .any(|e| matches!(e.dec, Deny | DenyLog | DenySyslog | DenyAudit))
}

fn any_allows_for_subject(p: &str, events: &[Event]) -> bool {
    events
        .iter()
        .filter(|e| matches!(e.subj.exe(), Some(exe) if exe == p))
        .any(|e| matches!(e.dec, Allow | AllowLog | AllowSyslog | AllowAudit))
}
