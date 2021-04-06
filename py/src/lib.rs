use pyo3::prelude::*;

pub mod app;
pub mod svc;
pub mod syscheck;
pub mod trust;

#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    app::init_module(_py, m)?;
    trust::init_module(_py, m)?;
    Ok(())
}
