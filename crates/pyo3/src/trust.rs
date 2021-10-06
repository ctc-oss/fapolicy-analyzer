use pyo3::prelude::*;

use fapolicy_api::trust::Trust;
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

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyTrust>()?;
    m.add_class::<PyActual>()?;
    Ok(())
}
