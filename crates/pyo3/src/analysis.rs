/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::collections::HashSet;

use pyo3::prelude::*;

use fapolicy_analyzer::events::analysis::{analyze, Analysis, ObjAnalysis, SubjAnalysis};
use fapolicy_analyzer::events::db::DB as EventDB;
use fapolicy_analyzer::events::event::{Event, Perspective};
use fapolicy_trust::db::DB as TrustDB;

/// An Event parsed from a fapolicyd log
#[pyclass(module = "log", name = "Event")]
#[derive(Clone, Debug)]
pub struct PyEvent {
    rs: Analysis,
}
impl From<Analysis> for PyEvent {
    fn from(rs: Analysis) -> Self {
        Self { rs }
    }
}
impl From<PyEvent> for Analysis {
    fn from(py: PyEvent) -> Self {
        py.rs
    }
}

pub(crate) fn expand_on_gid(rs: &Analysis) -> Vec<PyEvent> {
    let mut r = vec![];
    for gid in &rs.event.gid {
        let e = rs.clone().event;
        r.push(PyEvent {
            rs: Analysis {
                event: Event {
                    gid: vec![*gid],
                    ..e
                },
                subject: rs.subject.clone(),
                object: rs.object.clone(),
            },
        })
    }
    r
}

#[pymethods]
impl PyEvent {
    /// The user id parsed from the log event
    #[getter]
    fn uid(&self) -> i32 {
        self.rs.event.uid
    }

    /// The group id parsed from the log event
    #[getter]
    fn gid(&self) -> i32 {
        *self.rs.event.gid.first().unwrap_or(&-1)
    }

    /// The fapolicyd subject parsed from the log event
    #[getter]
    fn subject(&self) -> PySubject {
        self.rs.subject.clone().into()
    }

    /// The fapolicyd object parsed from the log event
    #[getter]
    fn object(&self) -> PyObject {
        self.rs.object.clone().into()
    }

    /// The fapolicyd rule_id parsed from the log event
    #[getter]
    fn rule_id(&self) -> i32 {
        self.rs.event.rule_id
    }

    fn when(&self) -> Option<i64> {
        self.rs.event.when.map(|t| t.timestamp())
    }
}

/// Subject metadata
#[pyclass(module = "log", name = "Subject")]
#[derive(Clone)]
pub struct PySubject {
    rs: SubjAnalysis,
}

impl From<SubjAnalysis> for PySubject {
    fn from(rs: SubjAnalysis) -> Self {
        Self { rs }
    }
}
impl From<PySubject> for SubjAnalysis {
    fn from(py: PySubject) -> Self {
        py.rs
    }
}

#[pymethods]
impl PySubject {
    /// Path of the subject parsed from the log event
    #[getter]
    fn file(&self) -> String {
        self.rs.file.clone()
    }

    /// Trust source of the log event subject
    #[getter]
    fn trust(&self) -> String {
        self.rs.trust.clone()
    }

    /// Trust status of the log event subject
    #[getter]
    fn trust_status(&self) -> String {
        self.rs.status.clone()
    }

    /// Access status of the log event subject
    #[getter]
    fn access(&self) -> String {
        self.rs.access.clone()
    }
}

/// Object metadata
#[pyclass(module = "log", name = "Object")]
#[derive(Clone)]
pub struct PyObject {
    rs: ObjAnalysis,
}

impl From<ObjAnalysis> for PyObject {
    fn from(rs: ObjAnalysis) -> Self {
        Self { rs }
    }
}
impl From<PyObject> for ObjAnalysis {
    fn from(py: PyObject) -> Self {
        py.rs
    }
}

#[pymethods]
impl PyObject {
    /// Path of the object parsed from the log event
    #[getter]
    fn file(&self) -> String {
        self.rs.file.clone()
    }

    /// Trust source of the log event object
    #[getter]
    fn trust(&self) -> String {
        self.rs.trust.clone()
    }

    /// Trust status of the log event object
    #[getter]
    fn trust_status(&self) -> String {
        self.rs.status.clone()
    }

    /// Access status of the log event object
    #[getter]
    fn access(&self) -> String {
        self.rs.access.clone()
    }

    /// Perm flag from logged event
    #[getter]
    fn perm(&self) -> String {
        self.rs.perm.clone()
    }
}

#[pyclass(module = "log", name = "EventLog")]
#[derive(Clone)]
pub struct PyEventLog {
    pub(crate) rs: EventDB,
    pub(crate) rs_trust: TrustDB,
    start: Option<i64>,
    stop: Option<i64>,
}

impl PyEventLog {
    pub(crate) fn new(rs: EventDB, trust: TrustDB) -> Self {
        Self {
            rs,
            rs_trust: trust,
            start: None,
            stop: None,
        }
    }

    fn temporal_filter(&self, e: &PyEvent) -> bool {
        match (e.rs.event.when, self.start, self.stop) {
            (None, _, _) | (_, None, None) => true,
            (Some(t), Some(begin), None) => t.timestamp() >= begin,
            (Some(t), None, Some(end)) => t.timestamp() <= end,
            (Some(t), Some(begin), Some(end)) => t.timestamp() >= begin && t.timestamp() <= end,
        }
    }
}

#[pymethods]
impl PyEventLog {
    /// Get all subjects from the event log
    fn subjects(&self) -> Vec<String> {
        let m: HashSet<String> = self.rs.iter().filter_map(|e| e.subj.exe()).collect();
        m.into_iter().collect()
    }

    fn begin(&mut self, start: Option<i64>) {
        self.start = start;
    }

    fn until(&mut self, stop: Option<i64>) {
        self.stop = stop;
    }

    /// Get events that fit the given subject perspective perspective
    fn by_subject(&self, path: &str) -> Vec<PyEvent> {
        analyze(
            &self.rs,
            Perspective::Subject(path.to_string()),
            &self.rs_trust,
        )
        .iter()
        .flat_map(expand_on_gid)
        .filter(|e| self.temporal_filter(e))
        .collect()
    }

    /// Get events that fit the given user perspective
    fn by_user(&self, uid: i32) -> Vec<PyEvent> {
        analyze(&self.rs, Perspective::User(uid), &self.rs_trust)
            .iter()
            .flat_map(|e| expand_on_gid(e).into_iter().filter(|e| e.uid() == uid))
            .filter(|e| self.temporal_filter(e))
            .collect()
    }

    /// Get events that fit the given group perspective
    fn by_group(&self, gid: i32) -> Vec<PyEvent> {
        analyze(&self.rs, Perspective::Group(gid), &self.rs_trust)
            .iter()
            .flat_map(|e| expand_on_gid(e).into_iter().filter(|e| e.gid() == gid))
            .filter(|e| self.temporal_filter(e))
            .collect()
    }
}

pub fn init_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyEvent>()?;
    m.add_class::<PySubject>()?;
    m.add_class::<PyObject>()?;
    m.add_class::<PyEventLog>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::{DateTime, NaiveDateTime, Utc};
    use fapolicy_rules::{Decision, Object, Permission, Subject};

    const TEST_PATH: &str = "/bin/bash";

    fn events() -> EventDB {
        let t = Event {
            rule_id: 0,
            dec: Decision::AllowAudit,
            perm: Permission::Any,
            uid: 0,
            gid: vec![0],
            pid: 0,
            subj: Subject::from_exe(TEST_PATH),
            obj: Object::from_path(TEST_PATH),
            when: None,
        };
        let events = (0..=5)
            .map(|i| Event {
                rule_id: i,
                when: Some(DateTime::from_utc(
                    NaiveDateTime::from_timestamp(i as i64, 0),
                    Utc,
                )),
                ..t.clone()
            })
            .collect();
        EventDB::from(events)
    }

    #[test]
    fn temporal_filtering() {
        let e = events();
        let all = e.len();
        let mut log = PyEventLog {
            rs: e,
            rs_trust: Default::default(),
            start: Some(0),
            stop: Some(5),
        };
        assert_eq!(all, log.by_subject(TEST_PATH).len());

        log.begin(Some(1));
        assert_eq!(all - 1, log.by_subject(TEST_PATH).len());

        log.until(Some(4));
        assert_eq!(all - 2, log.by_subject(TEST_PATH).len());

        log.until(Some(3));
        assert_eq!(all - 3, log.by_subject(TEST_PATH).len());

        log.begin(Some(2));
        assert_eq!(all - 4, log.by_subject(TEST_PATH).len());

        log.begin(None);
        log.until(None);
        assert_eq!(all, log.by_subject(TEST_PATH).len());

        log.until(Some(3));
        assert_eq!(all - 2, log.by_subject(TEST_PATH).len());
    }
}
