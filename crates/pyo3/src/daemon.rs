use fapolicy_daemon::svc::Handle;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

#[pyclass(module = "svc", name = "Handle")]
#[derive(Clone)]
/// A handle to a systemd service.
pub struct PyHandle {
    rs: Handle,
}
impl From<Handle> for PyHandle {
    fn from(rs: Handle) -> Self {
        Self { rs }
    }
}
impl From<PyHandle> for Handle {
    fn from(py: PyHandle) -> Self {
        py.rs
    }
}

#[pymethods]
impl PyHandle {
    #[new]
    fn new(unit: String) -> PyResult<PyHandle> {
        Ok(PyHandle {
            rs: Handle::new(&unit),
        })
    }

    pub fn start(&self) -> PyResult<()> {
        self.rs
            .start()
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
    }

    pub fn stop(&self) -> PyResult<()> {
        self.rs
            .stop()
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
    }

    pub fn enable(&self) -> PyResult<()> {
        self.rs
            .enable()
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
    }

    pub fn disable(&self) -> PyResult<()> {
        self.rs
            .disable()
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
    }

    pub fn is_active(&self) -> PyResult<bool> {
        self.rs
            .active()
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
    }
}

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
fn is_fapolicyd_active() -> PyResult<bool> {
    fapolicy_daemon::svc::Handle::default()
        .active()
        .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyHandle>()?;
    m.add_function(wrap_pyfunction!(start_fapolicyd, m)?)?;
    m.add_function(wrap_pyfunction!(stop_fapolicyd, m)?)?;
    m.add_function(wrap_pyfunction!(is_fapolicyd_active, m)?)?;
    Ok(())
}
