use fapolicy_trust::db::DB as TrustDB;

use crate::error::Error;
use crate::error::Error::AnalyzerError;
use crate::events::db::DB as EventDB;
use crate::events::event::{Event, Perspective};
use fapolicy_rules::Decision::*;

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

pub fn analyze(db: &EventDB, from: Perspective, trust: &TrustDB) -> Vec<Analysis> {
    let fit_events: Vec<Event> = db.events.iter().cloned().filter(|e| from.fit(e)).collect();

    fit_events
        .iter()
        .map(|e| {
            let sp = e.subj.exe().unwrap();
            let op = e.obj.path().unwrap();

            let ed = match e.dec {
                Allow | AllowLog | AllowSyslog | AllowAudit => "A".to_string(),
                Deny | DenyLog | DenySyslog | DenyAudit => "D".to_string(),
            };

            let sa = match (
                any_allows_for_subject(&sp, &fit_events),
                any_denials_for_subject(&sp, &fit_events),
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

fn trust_check(path: &str, db: &TrustDB) -> Result<String, Error> {
    match db.get(path) {
        Some(r) if r.is_system() => Ok("ST".into()),
        Some(r) if r.is_ancillary() => Ok("AT".into()),
        None => Ok("U".into()),
        _ => Err(AnalyzerError("unexpected trust check state".into())),
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
