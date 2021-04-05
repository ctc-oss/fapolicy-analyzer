use pyo3::prelude::*;

use fapolicy_analyzer::api::TrustSource;
use fapolicy_analyzer::app::State;
use fapolicy_analyzer::cfg;
use fapolicy_analyzer::check::trust_status;

use super::trust::PyChangeTrust;
use super::trust::PyTrust;
use fapolicy_analyzer::sys::deploy_app_state;

#[pyclass(module = "app", name = "System")]
#[derive(Clone)]
pub struct PySystem {
    state: State,
}
impl From<State> for PySystem {
    fn from(state: State) -> Self {
        Self { state }
    }
}
impl From<PySystem> for State {
    fn from(s: PySystem) -> Self {
        s.state
    }
}

#[pymethods]
impl PySystem {
    #[new]
    fn new() -> PySystem {
        let conf = cfg::load();
        State::new(&conf.system).into()
    }

    fn system_trust(&self) -> PyResult<Vec<PyTrust>> {
        Ok(self
            .state
            .trust_db
            .iter()
            .filter(|t| t.source == TrustSource::System)
            .map(trust_status)
            .flatten()
            .map(|t| PyTrust::from(t.clone()))
            .collect())
    }

    fn ancillary_trust(&self) -> PyResult<Vec<PyTrust>> {
        Ok(self
            .state
            .trust_db
            .iter()
            .filter(|t| t.source == TrustSource::Ancillary)
            .map(trust_status)
            .flatten()
            .map(|t| PyTrust::from(t.clone()))
            .collect())
    }

    fn apply_changeset(&self, change: PyChangeTrust) -> PySystem {
        self.state.apply_trust_changes(change.into()).into()
    }

    fn deploy(&self) {
        deploy_app_state(&self.state);
    }

    fn is_stale(&self) -> bool {
        // todo;; check current state againt rpm and file
        false
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySystem>()?;
    Ok(())
}
