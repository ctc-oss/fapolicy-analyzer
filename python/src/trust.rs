use pyo3::prelude::*;

use fapolicy_analyzer::api;
use fapolicy_analyzer::api::TrustSource;
use fapolicy_analyzer::trust;

/// Trust entry
///
/// Includes the path, size, and sha256 hash
#[pyclass(module = "trust", name = "Trust")]
#[derive(Clone)]
pub struct PyTrust {
    pub trust: api::Trust,
    pub status: String,
}
impl From<trust::Status> for PyTrust {
    fn from(status: trust::Status) -> Self {
        let (trust, tag) = match status {
            trust::Status::Trusted(t) => (t, "T"),
            trust::Status::Discrepancy(t, _) => (t, "D"),
            trust::Status::Unknown(t) => (t, "U"),
        };
        Self {
            trust,
            status: tag.to_string(),
        }
    }
}

#[pymethods]
impl PyTrust {
    #[new]
    fn new(p: &str, sz: u64, sha: &str) -> PyTrust {
        PyTrust {
            trust: api::Trust {
                path: p.to_string(),
                size: sz,
                hash: sha.to_string(),
                source: TrustSource::Ancillary,
            },
            status: "U".to_string(),
        }
    }

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

    /// Get a string representation of the TDU status
    #[getter]
    fn get_status(&self) -> &str {
        &self.status
    }
}

/// A mutable collection of changes
#[pyclass(module = "trust", name = "Changeset")]
#[derive(Clone)]
pub struct PyChangeset {
    s: trust::Changeset,
}

impl From<trust::Changeset> for PyChangeset {
    fn from(s: trust::Changeset) -> Self {
        Self { s }
    }
}

impl From<PyChangeset> for trust::Changeset {
    fn from(s: PyChangeset) -> Self {
        s.s
    }
}

#[pymethods]
impl PyChangeset {
    #[new]
    pub fn new() -> Self {
        trust::Changeset::new().into()
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
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyTrust>()?;
    m.add_class::<PyChangeset>()?;
    // m.add_wrapped(pyo3::wrap_pyfunction!(apply_trust_change))?;
    Ok(())
}
