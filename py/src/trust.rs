use pyo3::prelude::*;

use fapolicy_analyzer::api;
use fapolicy_analyzer::api::TrustSource;
use fapolicy_analyzer::change;
use fapolicy_analyzer::trust;

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
            trust::Status::Untrusted(t, _) => (t, "U"),
            trust::Status::Unknown(t) => (t, "_"),
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
            status: "_".to_string(),
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

    #[getter]
    fn get_status(&self) -> &str {
        &self.status
    }
}

#[pyclass(module = "trust", name = "Changeset")]
#[derive(Clone)]
pub struct PyChangeTrust {
    s: change::TrustSet,
}

impl From<change::TrustSet> for PyChangeTrust {
    fn from(s: change::TrustSet) -> Self {
        Self { s }
    }
}

impl From<PyChangeTrust> for change::TrustSet {
    fn from(s: PyChangeTrust) -> Self {
        s.s
    }
}

#[pymethods]
impl PyChangeTrust {
    #[new]
    pub fn new() -> Self {
        change::TrustSet::empty().into()
    }

    pub fn add_trust(&mut self, path: &str) -> bool {
        self.s.add(path).is_err()
    }

    pub fn del_trust(&mut self, path: &str) -> bool {
        self.s.del(path).is_err()
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
    m.add_class::<PyChangeTrust>()?;
    // m.add_wrapped(pyo3::wrap_pyfunction!(apply_trust_change))?;
    Ok(())
}
