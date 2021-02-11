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

    fn dump_trust(&self) {
        for t in &self.s.trust {
            println!("{:?}", t);
        }
    }

    fn trust(&self) -> PyResult<Vec<PyTrust>> {
        Ok(self
            .s
            .trust
            .iter()
            .map(|t| PyTrust::from(t.clone()))
            .collect())
    }
}

#[pymodule]
fn app(_py: Python, m: &PyModule) -> PyResult<()> {
    // m.add_wrapped(pyo3::wrap_pyfunction!(parse_trust_entry))?;
    m.add_class::<PySystem>()?;
    Ok(())
}
