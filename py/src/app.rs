use pyo3::prelude::*;

use super::trust::PyTrust;
use fapolicy_analyzer::sys;

#[pyclass(module = "app", name=System)]
#[derive(Clone)]
pub struct PySystem {
    s: sys::System,
}
impl From<sys::System> for PySystem {
    fn from(s: sys::System) -> Self {
        Self { s }
    }
}
impl From<PySystem> for sys::System {
    fn from(s: PySystem) -> Self {
        s.s
    }
}

#[pymethods]
impl PySystem {
    #[new]
    fn new(ancillary_trust_path: Option<String>, system_trust_path: Option<String>) -> PySystem {
        sys::System::boot(sys::SystemCfg {
            system_trust_path,
            ancillary_trust_path,
        })
        .into()
    }

    fn system_trust(&self) -> PyResult<Vec<PyTrust>> {
        Ok(self
            .s
            .system_trust
            .iter()
            .map(|t| PyTrust::from(t.clone()))
            .collect())
    }

    fn ancillary_trust(&self) -> PyResult<Vec<PyTrust>> {
        Ok(self
            .s
            .ancillary_trust
            .iter()
            .map(|t| PyTrust::from(t.clone()))
            .collect())
    }
}

#[pymodule]
fn app(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySystem>()?;
    Ok(())
}
