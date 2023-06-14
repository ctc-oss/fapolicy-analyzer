use pyo3::prelude::*;

/// Indicates whether the audit capability is available on this platform
#[pyfunction]
fn is_audit_available() -> bool {
    false
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_audit_available, m)?)?;
    Ok(())
}
