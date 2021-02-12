use fapolicy_analyzer::svc;

use pyo3::prelude::*;

#[pyclass(module = "svc", name=Daemon)]
#[derive(Clone)]
pub struct PyDaemon {
    d: svc::Daemon,
}
impl From<svc::Daemon> for PyDaemon {
    fn from(d: svc::Daemon) -> Self {
        Self { d }
    }
}
impl From<PyDaemon> for svc::Daemon {
    fn from(d: PyDaemon) -> Self {
        d.d
    }
}

#[pymethods]
impl PyDaemon {
    #[new]
    fn new(unit_name: &str) -> PyDaemon {
        svc::Daemon::new(unit_name).into()
    }

    fn start(&self) {
        self.d.start().unwrap();
    }
    fn stop(&self) {
        self.d.stop().unwrap();
    }
}

#[pymodule]
fn svc(_py: Python, m: &PyModule) -> PyResult<()> {
    // m.add_wrapped(pyo3::wrap_pyfunction!(parse_trust_entry))?;
    m.add_class::<PyDaemon>()?;
    Ok(())
}
