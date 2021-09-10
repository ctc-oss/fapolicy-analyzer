use std::collections::HashMap;

use fapolicy_trust::ops::{get_path_action_map, Changeset};
use fapolicy_trust::stat::{Actual, Status};
use fapolicy_trust::trust::Trust;
use pyo3::prelude::*;

/// Trust entry
///
/// Includes the path, size, and sha256 hash
#[pyclass(module = "trust", name = "Trust")]
#[derive(Clone)]
pub struct PyTrust {
    pub trust: Trust,
    pub actual: Actual,
    pub status: String,
}
impl From<Status> for PyTrust {
    fn from(status: Status) -> Self {
        let (trust, actual, tag) = match status {
            Status::Trusted(t, act) => (t, act, "T"),
            Status::Discrepancy(t, act) => (t, act, "D"),
        };
        Self {
            trust,
            actual,
            status: tag.to_string(),
        }
    }
}

#[pymethods]
impl PyTrust {
    #[getter]
    fn get_size(&self) -> u64 {
        self.trust.size
    }

    #[getter]
    fn get_path(&self) -> &str {
        &self.trust.path
    }

    #[getter]
    fn get_hash(&self) -> &str {
        &self.trust.hash
    }

    #[getter]
    fn get_last_modified(&self) -> u64 {
        self.actual.last_modified
    }

    #[getter]
    fn get_status(&self) -> &str {
        &self.status
    }
}

/// A mutable collection of changes
#[pyclass(module = "trust", name = "Changeset")]
#[derive(Clone)]
pub struct PyChangeset {
    s: Changeset,
}

impl From<Changeset> for PyChangeset {
    fn from(s: Changeset) -> Self {
        Self { s }
    }
}

impl From<PyChangeset> for Changeset {
    fn from(s: PyChangeset) -> Self {
        s.s
    }
}

#[pymethods]
impl PyChangeset {
    #[new]
    pub fn new() -> Self {
        Changeset::new().into()
    }

    pub fn add_trust(&mut self, path: &str) {
        self.s.add(path)
    }

    pub fn del_trust(&mut self, path: &str) {
        self.s.del(path)
    }

    pub fn len(&self) -> usize {
        self.s.len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn get_path_action_map(&self) -> HashMap<String, String> {
        get_path_action_map(&self.s)
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyTrust>()?;
    m.add_class::<PyChangeset>()?;
    // m.add_wrapped(pyo3::wrap_pyfunction!(apply_trust_change))?;
    Ok(())
}
