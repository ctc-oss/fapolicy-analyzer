use crate::analysis::PyEvent;
use fapolicy_analyzer::events;
use fapolicy_analyzer::events::event::Event;
use pyo3::exceptions;
use pyo3::prelude::*;

/// Indicates whether the audit capability is available on this platform
#[pyfunction]
fn is_audit_available() -> bool {
    false
}

#[pyfunction]
fn parse_audit_log(path: String) -> Vec<String> {
    events::read::from_auditlog_file(&path)
        .expect("parse_audit_log pyo3")
        .into_iter()
        .map(|e| format!("{e:?}"))
        .collect()
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_audit_available, m)?)?;
    m.add_function(wrap_pyfunction!(parse_audit_log, m)?)?;
    Ok(())
}
