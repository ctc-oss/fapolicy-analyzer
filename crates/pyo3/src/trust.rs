/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use pyo3::exceptions::PyRuntimeError;
use std::collections::HashMap;

use fapolicy_daemon::pipe;
use pyo3::prelude::*;

use fapolicy_trust::ops::{get_path_action_map, Changeset};
use fapolicy_trust::stat::{Actual, Status};
use fapolicy_trust::Trust;

/// Trust entry
///
/// Includes the path, size, and sha256 hash
#[pyclass(module = "trust", name = "Trust")]
#[derive(Clone)]
pub struct PyTrust {
    pub rs_trust: Trust,
    pub rs_actual: Option<Actual>,
    pub status: String,
}
impl From<Status> for PyTrust {
    fn from(status: Status) -> Self {
        let (rs_trust, rs_actual, tag) = match status {
            Status::Trusted(t, act) => (t, Some(act), "T"),
            Status::Discrepancy(t, act) => (t, Some(act), "D"),
            Status::Missing(t) => (t, None, "U"),
        };
        Self {
            rs_trust,
            rs_actual,
            status: tag.to_string(),
        }
    }
}

// from trust, with no actual check
impl From<Trust> for PyTrust {
    fn from(t: Trust) -> Self {
        Self {
            rs_trust: t,
            rs_actual: None,
            status: "U".to_string(),
        }
    }
}

#[pymethods]
impl PyTrust {
    #[getter]
    fn get_path(&self) -> &str {
        &self.rs_trust.path
    }

    #[getter]
    fn get_size(&self) -> u64 {
        self.rs_trust.size
    }

    #[getter]
    fn get_hash(&self) -> &str {
        &self.rs_trust.hash
    }

    /// Optional actual metadata
    /// Will be None in the case of the file not existing
    #[getter]
    fn get_actual(&self) -> Option<PyActual> {
        self.rs_actual.as_ref().map(|a| a.clone().into())
    }

    #[getter]
    fn get_status(&self) -> &str {
        &self.status
    }
}

impl PyTrust {
    pub fn from_status_opt(o: Option<Status>, t: Trust) -> Self {
        match o {
            Some(status) => status.into(),
            None => t.into(),
        }
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(format!("[{}]\t{}", self.status, self.rs_trust))
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("[{}]\t{}", self.status, self.rs_trust))
    }
}

/// A collection of actual metadata about the trusted file
#[pyclass(module = "trust", name = "Actual")]
pub struct PyActual {
    rs: Actual,
}

impl From<Actual> for PyActual {
    fn from(rs: Actual) -> Self {
        Self { rs }
    }
}

impl From<PyActual> for Actual {
    fn from(py: PyActual) -> Self {
        py.rs
    }
}

#[pymethods]
impl PyActual {
    #[getter]
    fn get_size(&self) -> u64 {
        self.rs.size
    }

    #[getter]
    fn get_hash(&self) -> &str {
        &self.rs.hash
    }

    #[getter]
    fn get_last_modified(&self) -> u64 {
        self.rs.last_modified
    }
}

/// A mutable collection of changes
#[pyclass(module = "trust", name = "Changeset")]
#[derive(Clone)]
pub struct PyChangeset {
    rs: Changeset,
}

impl From<Changeset> for PyChangeset {
    fn from(rs: Changeset) -> Self {
        Self { rs }
    }
}

impl From<PyChangeset> for Changeset {
    fn from(py: PyChangeset) -> Self {
        py.rs
    }
}

impl Default for PyChangeset {
    fn default() -> Self {
        Changeset::new().into()
    }
}

#[pymethods]
impl PyChangeset {
    #[new]
    pub fn new() -> Self {
        PyChangeset::default()
    }

    pub fn add_trust(&mut self, path: &str) {
        self.rs.add(path)
    }

    pub fn del_trust(&mut self, path: &str) {
        self.rs.del(path)
    }

    pub fn len(&self) -> usize {
        self.rs.len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn get_path_action_map(&self) -> HashMap<String, String> {
        get_path_action_map(&self.rs)
    }
}

/// send signal to fapolicyd FIFO pipe to reload the trust database
#[pyfunction]
fn signal_trust_reload() -> PyResult<()> {
    pipe::reload_trust()
        .map_err(|e| PyRuntimeError::new_err(format!("failed to signal trust reload: {:?}", e)))
}

/// send signal to fapolicyd FIFO pipe to reload rules
#[pyfunction]
fn signal_rule_reload() -> PyResult<()> {
    pipe::reload_rules()
        .map_err(|e| PyRuntimeError::new_err(format!("failed to signal rules reload: {:?}", e)))
}

pub fn init_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyChangeset>()?;
    m.add_class::<PyTrust>()?;
    m.add_class::<PyActual>()?;
    m.add_function(wrap_pyfunction!(signal_trust_reload, m)?)?;
    m.add_function(wrap_pyfunction!(signal_rule_reload, m)?)?;
    Ok(())
}
