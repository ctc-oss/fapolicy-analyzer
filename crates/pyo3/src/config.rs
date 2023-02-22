use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

use fapolicy_app::cfg;

/// Provide path to the application config file
#[pyfunction]
fn config_file_path() -> PyResult<String> {
    cfg::All::config_dir()
        .map(|p| p.display().to_string())
        .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(config_file_path, m)?)?;
    Ok(())
}
