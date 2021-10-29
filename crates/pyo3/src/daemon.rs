use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

#[pyfunction]
fn start_fapolicyd() -> PyResult<()> {
    match fapolicy_daemon::svc::Handle::default().start() {
        Ok(_) => {
            println!("starting fapolicyd daemon");
            Ok(())
        }
        Err(e) => Err(PyRuntimeError::new_err(format!("{:?}", e))),
    }
}

#[pyfunction]
fn stop_fapolicyd() -> PyResult<()> {
    match fapolicy_daemon::svc::Handle::default().stop() {
        Ok(_) => {
            println!("stopped fapolicyd daemon");
            Ok(())
        }
        Err(e) => Err(PyRuntimeError::new_err(format!("{:?}", e))),
    }
}

#[pyfunction]
fn is_active() -> PyResult<bool> {
    fapolicy_daemon::svc::Handle::default()
        .active()
        .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(start_fapolicyd, m)?)?;
    m.add_function(wrap_pyfunction!(stop_fapolicyd, m)?)?;
    m.add_function(wrap_pyfunction!(is_active, m)?)?;
    Ok(())
}
