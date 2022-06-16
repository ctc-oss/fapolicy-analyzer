/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use pyo3::prelude::*;
use pyo3::{exceptions, PyResult};

use fapolicy_analyzer::events;
use fapolicy_analyzer::events::db::DB as EventDB;
use fapolicy_app::app::State;
use fapolicy_app::cfg;
use fapolicy_app::sys::deploy_app_state;
use fapolicy_rules::db::RuleDef;

use super::trust::PyTrust;
use crate::acl::{PyGroup, PyUser};
use crate::analysis::PyEventLog;
use crate::rules;
use crate::rules::PyRule;
use crate::trust;

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
            match State::load_checked(&conf) {
                Ok(state) => Ok(state.into()),
                Err(e) => Err(exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
            }
        })
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
        self.deploy_only().and_then(|_| {
            fapolicy_daemon::reload_databases()
                .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))
        })
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
        Ok(PyEventLog {
            rs: EventDB::from(xs),
            rs_trust: self.rs.trust_db.clone(),
        })
    }

    /// Parse events from syslog at the specified path
    fn load_syslog(&self) -> PyResult<PyEventLog> {
        let xs = events::read::from_syslog(&self.rs.config.system.syslog_file_path)
            .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
        Ok(PyEventLog {
            rs: EventDB::from(xs),
            rs_trust: self.rs.trust_db.clone(),
        })
    }

    fn rules(&self) -> PyResult<Vec<PyRule>> {
        Ok(self
            .rs
            .rules_db
            .iter()
            .map(|(id, r)| {
                let (valid, text, info) = match r {
                    RuleDef::Invalid { text, error } => {
                        (false, text.clone(), vec![("e".to_string(), error.clone())])
                    }
                    RuleDef::Valid(r) => (true, r.to_string(), vec![]),
                    RuleDef::ValidWithWarning(r, w) => {
                        (true, r.to_string(), vec![("w".to_string(), w.clone())])
                    }
                };
                let origin = self
                    .rs
                    .rules_db
                    .source(*id)
                    // todo;; this should be converted to a python exception
                    .unwrap_or_else(|| "<unknown>".to_string());

                PyRule::new(*id, text, origin, info, valid)
            })
            .collect())
    }

    fn rules_text(&self) -> PyResult<String> {
        self.rules()
            .map(|x| {
                x.into_iter().fold((None, String::new()), |x, r| match x {
                    // no origin established yet
                    (None, _) => (
                        Some(r.origin.clone()),
                        format!("[{}]\n{}", r.origin, r.text),
                    ),
                    // same origin as previous
                    (Some(last_origin), acc_text) if last_origin == r.origin => {
                        (Some(last_origin), format!("{}\n{}", acc_text, r.text))
                    }
                    // origin has changed
                    (Some(_), acc_text) => (
                        Some(r.origin.clone()),
                        format!("{}\n\n[{}]\n{}", acc_text, r.origin, r.text),
                    ),
                })
            })
            .map(|(_, s)| s)
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySystem>()?;
    Ok(())
}
