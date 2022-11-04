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
        // todo;; unhack this
        *self.rs.event.gid.get(0).unwrap()
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

    /// Mode of the log event object
    #[getter]
    fn mode(&self) -> String {
        self.rs.mode.clone()
    }
}

#[pyclass(module = "log", name = "EventLog")]
#[derive(Clone)]
pub struct PyEventLog {
    pub(crate) rs: EventDB,
    pub(crate) rs_trust: TrustDB,
    start: Option<usize>,
    stop: Option<usize>,
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
}

#[pymethods]
impl PyEventLog {
    /// Get all subjects from the event log
    fn subjects(&self) -> Vec<String> {
        let m: HashSet<String> = self.rs.iter().filter_map(|e| e.subj.exe()).collect();
        m.into_iter().collect()
    }

    fn within(&self, start: usize, stop: usize) -> PyEventLog {
        let mut other = self.clone();
        other.start = Some(start);
        other.stop = Some(stop);
        other
    }

    fn from(&self, start: usize) -> PyEventLog {
        let mut other = self.clone();
        other.start = Some(start);
        other
    }

    fn until(&self, stop: usize) -> PyEventLog {
        let mut other = self.clone();
        other.stop = Some(stop);
        other
    }

    /// Get events that fit the given subject perspective perspective
    fn by_subject(&self, path: String) -> Vec<PyEvent> {
        analyze(&self.rs, Perspective::Subject(path), &self.rs_trust)
            .iter()
            .flat_map(|e| expand_on_gid(e))
            .collect()
    }

    /// Get events that fit the given user perspective
    fn by_user(&self, uid: i32) -> Vec<PyEvent> {
        analyze(&self.rs, Perspective::User(uid), &self.rs_trust)
            .iter()
            .flat_map(|e| expand_on_gid(e).into_iter().filter(|e| e.uid() == uid))
            .collect()
    }

    /// Get events that fit the given group perspective
    fn by_group(&self, gid: i32) -> Vec<PyEvent> {
        analyze(&self.rs, Perspective::Group(gid), &self.rs_trust)
            .iter()
            .flat_map(|e| expand_on_gid(e).into_iter().filter(|e| e.gid() == gid))
            .collect()
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyEvent>()?;
    m.add_class::<PySubject>()?;
    m.add_class::<PyObject>()?;
    m.add_class::<PyEventLog>()?;
    Ok(())
}
