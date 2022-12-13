/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use pyo3::prelude::*;
use pyo3::{exceptions, PyResult};
use similar::{ChangeTag, TextDiff};
use std::sync::mpsc;
use std::thread;

use fapolicy_analyzer::events;
use fapolicy_analyzer::events::db::DB as EventDB;
use fapolicy_app::app::State;
use fapolicy_app::cfg;
use fapolicy_app::sys::deploy_app_state;
use fapolicy_trust::stat::Status::*;
use fapolicy_trust::stat::{check, Status};

use super::trust::PyTrust;
use crate::acl::{PyGroup, PyUser};
use crate::analysis::PyEventLog;
use crate::rules::PyRule;
use crate::trust;
use crate::{daemon, rules};

#[pyclass(module = "app", name = "System")]
#[derive(Clone)]
/// An immutable view of host system state.
/// This only a container for state, it has to be applied to the host system.
pub struct PySystem {
    rs: State,
}
impl From<State> for PySystem {
    fn from(rs: State) -> Self {
        Self { rs }
    }
}
impl From<PySystem> for State {
    fn from(py: PySystem) -> Self {
        py.rs
    }
}

enum Update {
    Items(Vec<Status>),
    Done,
}

#[pymethods]
impl PySystem {
    /// Create a new initialized System
    /// This returns a result object that will be an error if initialization fails,
    /// allowing the member accessors on the System to return non-result objects.
    #[new]
    fn new(py: Python) -> PyResult<PySystem> {
        py.allow_threads(|| {
            let conf = cfg::All::load()
                .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
            match State::load(&conf) {
                Ok(state) => Ok(state.into()),
                Err(e) => Err(exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
            }
        })
    }

    fn merge(&mut self, trust: Vec<PyTrust>) {
        for t in trust {
            if let Some(e) = self.rs.trust_db.get_mut(&t.rs_trust.path) {
                match (t.status.as_str(), t.rs_actual) {
                    ("T", Some(a)) => e.status = Some(Trusted(t.rs_trust, a)),
                    ("D", Some(a)) => e.status = Some(Discrepancy(t.rs_trust, a)),
                    ("U", None) => e.status = Some(Missing(t.rs_trust)),
                    _ => {}
                }
            }
        }
    }

    /// Obtain a list of trusted files sourced from the system trust database.
    /// The system trust is generated from the contents of the RPM database.
    /// This represents state in the current fapolicyd database, not necessarily
    /// matching what is currently in the RPM database.
    fn system_trust(&self) -> Vec<PyTrust> {
        self.rs
            .trust_db
            .values()
            .iter()
            .filter(|r| r.is_system())
            .filter_map(|r| r.status.clone())
            .map(PyTrust::from)
            .collect()
    }

    /// Obtain a list of trusted files sourced from the ancillary trust database.
    /// This represents state in the current fapolicyd database, not necessarily
    /// matching what is currently in the ancillary trust file.
    fn ancillary_trust(&self) -> Vec<PyTrust> {
        self.rs
            .trust_db
            .values()
            .iter()
            .filter(|r| r.is_ancillary())
            .filter_map(|r| r.status.clone())
            .map(PyTrust::from)
            .collect()
    }

    /// Apply the changeset to the state of this System, produces a new System
    fn apply_changeset(&self, change: trust::PyChangeset) -> PySystem {
        self.rs.apply_trust_changes(change.into()).into()
    }

    /// Apply the changeset to the state of this System, produces a new System
    fn apply_rule_changes(&self, change: rules::PyChangeset) -> PySystem {
        self.rs.apply_rule_changes(change.into()).into()
    }

    /// Update the host system with this state of this System and signal fapolicyd to reload trust
    pub fn deploy(&self) -> PyResult<()> {
        daemon::deploy(self).map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))
    }

    /// Update the host system with this state of this System
    pub fn deploy_only(&self) -> PyResult<()> {
        deploy_app_state(&self.rs)
            .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))
    }

    /// Check the host system state against the state of this System
    fn is_stale(&self) -> bool {
        // todo;; check current state againt rpm and file
        false
    }

    /// Load a list of system users
    fn users(&self) -> Vec<PyUser> {
        self.rs.users.iter().map(|u| u.clone().into()).collect()
    }

    /// Load a list of system groups
    fn groups(&self) -> Vec<PyGroup> {
        self.rs.groups.iter().map(|g| g.clone().into()).collect()
    }

    /// Parse events from debug mode log at the specified path
    fn load_debuglog(&self, log: &str) -> PyResult<PyEventLog> {
        let xs = events::read::from_debug(log)
            .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
        Ok(PyEventLog::new(EventDB::from(xs), self.rs.trust_db.clone()))
    }

    /// Parse events from syslog at the specified path
    fn load_syslog(&self) -> PyResult<PyEventLog> {
        let xs = events::read::from_syslog(&self.rs.config.system.syslog_file_path)
            .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
        Ok(PyEventLog::new(EventDB::from(xs), self.rs.trust_db.clone()))
    }

    fn rules(&self) -> Vec<PyRule> {
        rules::to_vec(&self.rs.rules_db)
    }

    fn rules_text(&self) -> String {
        rules::to_text(&self.rs.rules_db)
    }
}

#[pyfunction]
fn rules_difference(lhs: &PySystem, rhs: &PySystem) -> String {
    let ltxt = lhs.rules_text();
    let rtxt = rhs.rules_text();
    let diff = TextDiff::from_lines(&ltxt, &rtxt);

    let mut diff_lines = vec![];
    for line in diff.iter_all_changes() {
        let sign = match line.tag() {
            ChangeTag::Delete => "-",
            ChangeTag::Insert => "+",
            ChangeTag::Equal => " ",
        };
        diff_lines.push(format!("{}{}", sign, line));
    }
    diff_lines.join("")
}

#[pyfunction]
fn check_disk_trust(db: &PySystem, update: PyObject, done: PyObject) -> PyResult<()> {
    let recs: Vec<_> = db
        .rs
        .trust_db
        .values()
        .into_iter()
        .map(|r| r.clone())
        .collect();

    let (tx, rx) = mpsc::channel();

    let chunks = recs.chunks(5);
    let total_chunks = chunks.len();

    let mut handles = vec![];
    for chunk in chunks {
        let ttx = tx.clone();
        let recs = chunk.to_vec();
        let t = thread::spawn(move || {
            println!("spawned");
            let updates = recs
                .into_iter()
                .flat_map(|r| check(&r.trusted))
                .collect::<Vec<_>>();
            ttx.send(Update::Items(updates));
            println!("shutdown check thread");
        });
        handles.push(t);
    }

    let ttx = tx.clone();
    thread::spawn(move || {
        for handle in handles {
            handle.join();
        }
        ttx.send(Update::Done);
        println!("shutdown done thread");
    });

    thread::spawn(move || {
        let mut cnt = 0;
        loop {
            if let Ok(u) = rx.recv() {
                match u {
                    Update::Items(i) => {
                        cnt += 1;
                        let r: Vec<_> = i.into_iter().map(PyTrust::from).collect();
                        Python::with_gil(|py| {
                            if update.call1(py, (r,)).is_err() {
                                eprintln!("failed make 'update' callback");
                            }
                        });
                    }
                    Update::Done => break,
                };
            }
        }

        Python::with_gil(|py| {
            if done.call0(py).is_err() {
                eprintln!("failed to make 'done' callback");
            }
        });
        println!("shutdown callback thread");
    });

    Ok(())
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySystem>()?;
    m.add_function(wrap_pyfunction!(rules_difference, m)?)?;
    m.add_function(wrap_pyfunction!(check_disk_trust, m)?)?;
    Ok(())
}
