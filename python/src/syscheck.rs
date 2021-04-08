use pyo3::prelude::*;

use fapolicy_analyzer::rpm::check_rpm;

#[pyfunction]
fn syscheck_rpm() {
    match check_rpm() {
        Ok(v) => println!("- {} OK", v),
        Err(e) => println!("- RPM {:?} FAIL", e),
    }
}

#[pymodule]
fn syscheck(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(pyo3::wrap_pyfunction!(syscheck_rpm))?;
    Ok(())
}
