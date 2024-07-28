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

use fapolicy_analyzer::events;
use fapolicy_analyzer::events::db::DB as EventDB;
use fapolicy_app::app::State;
use fapolicy_app::cfg;
use fapolicy_app::sys::deploy_app_state;
use fapolicy_rules::db::Entry::Comment;
use fapolicy_trust::stat::Status::*;
use fapolicy_util::sha::sha256_digest;
// use fapolicy_util::sha::sha256_digest;

use crate::acl::{PyGroup, PyUser};
use crate::analysis::PyEventLog;
use crate::daemon::PyConfigInfo;
use crate::rules::PyRule;
use crate::trust;
use crate::{daemon, rules};

use super::trust::{PyFilterChangeset, PyFilterInfo, PyTrust};

#[pyclass(module = "app", name = "System")]
#[derive(Clone)]
/// An immutable view of host system state.
/// This only a container for state, it has to be applied to the host system.
pub struct PySystem {
    pub(crate) rs: State,
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
    /// Create a new uninitialized System
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

    /// Obtain a list of trusted files sourced from the system trust database.
    /// The system trust is generated from the contents of the RPM database.
    /// This represents state in the current fapolicyd database, not necessarily
    /// matching what is currently in the RPM database.
    fn system_trust(&self) -> Vec<PyTrust> {
        log::debug!("system_trust");
        self.rs
            .trust_db
            .values()
            .iter()
            .filter(|r| r.is_system())
            .map(|r| PyTrust::from_status_opt(r.status.clone(), r.trusted.clone()))
            .collect()
    }

    /// Obtain a list of trusted files sourced from the ancillary trust database.
    /// This represents state in the current fapolicyd database, not necessarily
    /// matching what is currently in the ancillary trust file.
    fn ancillary_trust(&self) -> Vec<PyTrust> {
        log::debug!("ancillary_trust");
        self.rs
            .trust_db
            .values()
            .iter()
            .filter(|r| r.is_ancillary())
            .map(|r| PyTrust::from_status_opt(r.status.clone(), r.trusted.clone()))
            .collect()
    }

    /// Apply the changeset to the state of this System, produces a new System
    fn apply_changeset(&self, change: trust::PyChangeset) -> PySystem {
        log::debug!("apply_changeset");
        self.rs.apply_trust_changes(change.into()).into()
    }

    /// Apply the changeset to the state of this System, produces a new System
    fn apply_rule_changes(&self, change: rules::PyChangeset) -> PySystem {
        log::debug!("apply_rule_changes");
        self.rs.apply_rule_changes(change.into()).into()
    }

    /// Apply the changeset to the state of this System, produces a new System
    fn apply_config_changes(&self, change: daemon::PyChangeset) -> PySystem {
        log::debug!("apply_config_changes");
        self.rs.apply_config_changes(change.into()).into()
    }

    /// Apply the changeset to the state of this System, produces a new System
    fn apply_trust_filter_changes(&self, change: PyFilterChangeset) -> PySystem {
        log::debug!("apply_trust_filter_changes");
        self.rs.apply_trust_filter_changes(change.into()).into()
    }

    /// Update the host system with this state of this System and signal fapolicyd to reload trust
    pub fn deploy(&self) -> PyResult<()> {
        log::debug!("deploy");
        daemon::deploy(self).map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))
    }

    /// Update the host system with this state of this System
    pub fn deploy_only(&self) -> PyResult<()> {
        log::debug!("deploy_only");
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
        log::debug!("users");
        self.rs.users.iter().map(|u| u.clone().into()).collect()
    }

    /// Load a list of system groups
    fn groups(&self) -> Vec<PyGroup> {
        log::debug!("groups");
        self.rs.groups.iter().map(|g| g.clone().into()).collect()
    }

    /// Parse events from debug mode log at the specified path
    fn load_debuglog(&self, log: &str) -> PyResult<PyEventLog> {
        log::debug!("load_debuglog");
        let xs = events::read::from_debug(log)
            .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
        Ok(PyEventLog::new(EventDB::from(xs), self.rs.trust_db.clone()))
    }

    /// Parse events from syslog at the specified path
    fn load_syslog(&self) -> PyResult<PyEventLog> {
        log::debug!("load_syslog");
        let xs = events::read::from_syslog(&self.rs.config.system.syslog_file_path)
            .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
        Ok(PyEventLog::new(EventDB::from(xs), self.rs.trust_db.clone()))
    }

    /// Parse events from the kernel audit log
    fn load_auditlog(&self) -> PyResult<PyEventLog> {
        log::debug!("load_auditlog");
        let xs = events::read::from_auditlog()
            .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
        Ok(PyEventLog::new(EventDB::from(xs), self.rs.trust_db.clone()))
    }

    fn rules(&self) -> Vec<PyRule> {
        log::debug!("rules");
        rules::to_vec(&self.rs.rules_db)
    }

    fn rules_text(&self) -> String {
        log::debug!("rules_text");
        rules::to_text(&self.rs.rules_db)
    }

    fn config_text(&self) -> String {
        log::debug!("config_text");
        daemon::conf_to_text(&self.rs.daemon_config)
    }

    fn trust_filter_text(&self) -> String {
        log::debug!("trust_filter_text");
        trust::filter_to_text(&self.rs.trust_filter_config)
    }

    fn config_info(&self) -> Vec<PyConfigInfo> {
        log::debug!("config_info");
        daemon::conf_info(&self.rs.daemon_config)
    }

    fn trust_filter_info(&self) -> Vec<PyFilterInfo> {
        log::debug!("trust_filter_info");
        trust::filter_info(&self.rs.trust_filter_config)
    }

    // we rely on the gil to keep this synced up
    fn merge(&mut self, trust: Vec<PyTrust>) {
        log::trace!("merging {} entries", trust.len());
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
}

// todo;; this will become more advanced and based on the config object rather than text
#[pyfunction]
fn config_difference(lhs: &PySystem, rhs: &PySystem) -> String {
    log::debug!("config_difference");

    let ltxt = lhs.config_text();
    let rtxt = rhs.config_text();
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

// todo;; this will become more advanced and based on the filter object rather than text
#[pyfunction]
fn trust_filter_difference(lhs: &PySystem, rhs: &PySystem) -> String {
    log::debug!("trust_filter_difference");

    let ltxt = lhs.trust_filter_text();
    let rtxt = rhs.trust_filter_text();
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

// todo;; this should become more advanced and be based on rule db rather than text
#[pyfunction]
fn rules_difference(lhs: &PySystem, rhs: &PySystem) -> String {
    log::debug!("rules_difference");

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

/// Creates a [PySystem] that has all trust entries checked against disk
#[pyfunction]
fn checked_system(py: Python) -> PyResult<PySystem> {
    py.allow_threads(|| {
        let conf = cfg::All::load()
            .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
        match State::load_checked(&conf) {
            Ok(state) => Ok(state.into()),
            Err(e) => Err(exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
        }
    })
}

/// Generate a sha256 hash of the db text
/// The text hashed here is the same as what would be written to
/// compiled.rules by either fapolicyd or the analyzer
#[pyfunction]
pub fn rule_identity(system: &PySystem) -> PyResult<String> {
    let txt = system
        .rs
        .rules_db
        .iter()
        .fold(String::new(), |acc, (_, (_, x))| match x {
            Comment(_) => acc,
            e => format!("{}\n{}\n", acc, crate::rules::text_for_entry(e)),
        });
    sha256_digest(txt.as_bytes())
        .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySystem>()?;
    m.add_function(wrap_pyfunction!(config_difference, m)?)?;
    m.add_function(wrap_pyfunction!(rules_difference, m)?)?;
    m.add_function(wrap_pyfunction!(trust_filter_difference, m)?)?;
    m.add_function(wrap_pyfunction!(checked_system, m)?)?;
    m.add_function(wrap_pyfunction!(rule_identity, m)?)?;
    Ok(())
}
