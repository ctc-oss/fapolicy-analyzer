use std::str::FromStr;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

use fapolicyd::trust::TrustEntry;

#[pyclass(module = "fapolicy_analyzer", name=TrustEntry)]
#[derive(Clone)]
pub struct PyTrustEntry {
    e: TrustEntry,
}
impl From<TrustEntry> for PyTrustEntry {
    fn from(e: TrustEntry) -> Self {
        Self { e }
    }
}
impl From<PyTrustEntry> for TrustEntry {
    fn from(e: PyTrustEntry) -> Self {
        e.e
    }
}

#[pyfunction]
pub fn parse_trust_entry(_py: Python, s: &str) -> PyResult<PyTrustEntry> {
    let e = TrustEntry::from_str(s).unwrap();
    Ok(PyTrustEntry { e })
}

#[pymethods]
impl PyTrustEntry {
    #[new]
    fn new(path: &str, size: i64, hash: &str) -> PyTrustEntry {
        TrustEntry::new(path, size, hash).into()
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
    fn get_hash(&self) -> PyResult<&str> {
        Ok(self.e.hash.as_str())
    }
}

#[pymodule]
fn trust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(pyo3::wrap_pyfunction!(parse_trust_entry))?;
    m.add_class::<PyTrustEntry>()?;
    Ok(())
}
