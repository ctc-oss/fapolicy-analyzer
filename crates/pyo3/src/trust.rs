use std::collections::HashMap;

use pyo3::prelude::*;

use fapolicy_api::trust::Trust;
use fapolicy_trust::ops::{get_path_action_map, Changeset};
use fapolicy_trust::stat::{Actual, Status};

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

#[pymethods]
impl PyChangeset {
    #[new]
    pub fn new() -> Self {
        Changeset::new().into()
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

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyTrust>()?;
    m.add_class::<PyActual>()?;
    m.add_class::<PyChangeset>()?;
    Ok(())
}
