use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

use std::str::FromStr;

use fapolicyd::trust::TrustEntry;

#[pyclass]
struct PyTrustEntry {
    #[pyo3(get)]
    pub path: String,
    #[pyo3(get)]
    pub size: i64,
    #[pyo3(get)]
    pub hash: String,
}

#[pyfunction]
fn parse_trust_entry(_py: Python, s: &str) -> PyResult<PyTrustEntry> {
    let e = TrustEntry::from_str(s).unwrap();
    Ok(PyTrustEntry {
        path: e.path,
        size: e.size,
        hash: e.hash,
    })
}

#[pymodule]
/// Module documentation string
fn fapolicy_analyzer(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(parse_trust_entry))?;
    m.add_class::<PyTrustEntry>()?;
    Ok(())
}
