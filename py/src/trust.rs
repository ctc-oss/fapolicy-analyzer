use fapolicy_analyzer::api;

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

#[pymethods]
impl PyTrust {
    #[new]
    fn new(path: &str, size: u64, hash: &str) -> PyTrust {
        api::Trust::new(path, size, hash, api::TrustSource::Ancillary).into()
    }

    #[getter]
    fn get_size(&self) -> PyResult<u64> {
        Ok(self.e.size)
    }

    #[getter]
    fn get_path(&self) -> PyResult<&str> {
        Ok(&self.e.path)
    }

    #[getter]
    fn get_hash(&self) -> PyResult<Option<&str>> {
        Ok(self.e.hash.as_deref())
    }
}

#[pymodule]
fn trust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyTrust>()?;
    Ok(())
}
