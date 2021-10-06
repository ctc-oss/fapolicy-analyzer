use pyo3::prelude::*;

pub mod acl;
pub mod analysis;
pub mod change;
pub mod system;
pub mod trust;

#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    acl::init_module(_py, m)?;
    analysis::init_module(_py, m)?;
    change::init_module(_py, m)?;
    system::init_module(_py, m)?;
    trust::init_module(_py, m)?;
    Ok(())
}
