use fapolicy_analyzer::api;
use fapolicy_analyzer::trust;

use pyo3::prelude::*;

#[pyclass(module = "trust", name=Trust)]
#[derive(Clone)]
pub struct PyTrust {
    e: api::Trust,
}
impl From<api::Trust> for PyTrust {
    fn from(e: api::Trust) -> Self {
        Self { e }
    }
}
impl From<PyTrust> for api::Trust {
    fn from(e: PyTrust) -> Self {
        e.e
    }
}

#[pyfunction]
pub fn parse_trust_entry(_py: Python, s: &str) -> PyResult<PyTrust> {
    let e = trust::parse_trust_record(s).unwrap();
    Ok(PyTrust { e })
}

#[pymethods]
impl PyTrust {
    #[new]
    fn new(path: &str, size: i64, hash: &str) -> PyTrust {
        api::Trust::new(path, size, hash, api::TrustSource::Ancillary).into()
    }

    #[getter]
    fn get_size(&self) -> PyResult<i64> {
        Ok(self.e.size)
    }

    #[getter]
    fn get_path(&self) -> PyResult<&str> {
        Ok(&self.e.path.as_str())
    }

    #[getter]
    fn get_hash(&self) -> PyResult<Option<&str>> {
        Ok(self.e.hash.as_deref())
    }
}

#[pymodule]
fn trust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(pyo3::wrap_pyfunction!(parse_trust_entry))?;
    m.add_class::<PyTrust>()?;
    Ok(())
}
