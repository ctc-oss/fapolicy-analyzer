use pyo3::prelude::*;

pub mod acl;
pub mod app;
pub mod event;
pub mod trust;

#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    acl::init_module(_py, m)?;
    app::init_module(_py, m)?;
    event::init_module(_py, m)?;
    trust::init_module(_py, m)?;
    Ok(())
}
