use fapolicy_analyzer::api;
use fapolicy_analyzer::trust;

use pyo3::prelude::*;

#[pyclass(module = "trust", name=Trust)]
#[derive(Clone)]
pub struct PyTrust {
    trust: api::Trust,
    status: String,
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
    #[getter]
    fn get_size(&self) -> PyResult<u64> {
        Ok(self.trust.size)
    }

    #[getter]
    fn get_path(&self) -> PyResult<&str> {
        Ok(&self.trust.path)
    }

    #[getter]
    fn get_hash(&self) -> PyResult<&str> {
        Ok(&self.trust.hash)
    }

    #[getter]
    fn get_status(&self) -> PyResult<&str> {
        Ok(&self.status)
    }
}

#[pymodule]
fn trust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyTrust>()?;
    Ok(())
}
