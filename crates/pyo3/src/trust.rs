/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use fapolicy_daemon::pipe;
use fapolicy_trust::filter::load::with_error_message;
use fapolicy_trust::filter::ops::Changeset as FilterChangeset;
use fapolicy_trust::filter::Line;
use fapolicy_trust::ops::{get_path_action_map, Changeset};
use fapolicy_trust::stat::{Actual, Status};
use fapolicy_trust::{filter, Trust};
use pyo3::exceptions;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use std::collections::HashMap;

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

pub(crate) fn filter_to_text(db: &filter::DB) -> String {
    db.iter()
        .fold(String::new(), |acc, line| format!("{acc}\n{line}"))
        .trim_start()
        .to_owned()
}

#[pyclass(module = "trust", name = "FilterInfo")]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct PyFilterInfo {
    pub category: String,
    pub message: String,
}

#[pymethods]
impl PyFilterInfo {
    #[getter]
    fn get_category(&self) -> String {
        self.category.clone()
    }

    #[getter]
    fn get_message(&self) -> String {
        self.message.clone()
    }
}

pub(crate) fn filter_info(db: &filter::DB) -> Vec<PyFilterInfo> {
    let e = "e";
    let w = "w";
    db.iter().fold(vec![], |mut acc, line| {
        let info = match line {
            Line::Invalid(s) => Some((e, format!("Invalid: {s}"))),
            Line::Malformed(s) => Some((e, format!("Malformed: {s}"))),
            Line::Duplicate(s) => Some((e, format!("Duplicated: {s}"))),
            Line::ValidWithWarning(_, m) => Some((w, format!("{m}"))),
            _ => None,
        };
        if let Some((category, message)) = info {
            acc.push(PyFilterInfo {
                category: category.to_owned(),
                message,
            });
        };
        acc
    })
}

/// A mutable collection of trust filter changes
#[pyclass(module = "trust", name = "TrustFilterChangeset")]
#[derive(Default, Clone)]
pub struct PyFilterChangeset {
    rs: FilterChangeset,
}

impl From<FilterChangeset> for PyFilterChangeset {
    fn from(rs: FilterChangeset) -> Self {
        Self { rs }
    }
}

impl From<PyFilterChangeset> for FilterChangeset {
    fn from(py: PyFilterChangeset) -> Self {
        py.rs
    }
}

#[pymethods]
impl PyFilterChangeset {
    #[new]
    pub fn new() -> Self {
        PyFilterChangeset::default()
    }

    fn parse(&mut self, text: &str) -> PyResult<()> {
        match self.rs.set(text.trim()) {
            Ok(_) => Ok(()),
            Err(e) => Err(exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
        }
    }

    fn text(&self) -> Option<&str> {
        self.rs.src().map(|s| &**s)
    }

    fn filter_info(&self) -> Vec<PyFilterInfo> {
        filter_info(self.rs.get())
    }

    fn is_valid(&self) -> bool {
        self.rs.get().is_valid()
    }
}

#[pyfunction]
fn filter_text_error_check(txt: &str) -> Option<String> {
    match with_error_message(txt) {
        Ok(_) => None,
        Err(s) => Some(s),
    }
}

pub fn init_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyChangeset>()?;
    m.add_class::<PyTrust>()?;
    m.add_class::<PyActual>()?;
    m.add_class::<PyFilterChangeset>()?;
    m.add_class::<PyFilterInfo>()?;
    m.add_function(wrap_pyfunction!(filter_text_error_check, m)?)?;
    m.add_function(wrap_pyfunction!(signal_trust_reload, m)?)?;
    m.add_function(wrap_pyfunction!(signal_rule_reload, m)?)?;
    Ok(())
}
