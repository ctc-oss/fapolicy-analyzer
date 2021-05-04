use pyo3::prelude::*;

use fapolicy_analyzer::api::TrustSource;
use fapolicy_analyzer::app::State;
use fapolicy_analyzer::cfg;
use fapolicy_analyzer::check::trust_status;

use super::trust::PyChangeset;
use super::trust::PyTrust;
use fapolicy_analyzer::sys::deploy_app_state;

#[pyclass(module = "app", name = "System")]
#[derive(Clone)]
/// An immutable view of host system state.
/// This only a container for state, it has to be applied to the host system.
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
        let conf = cfg::All::load();
        State::load(&conf).into()
    }

    /// Obtain a list of trusted files sourced from the system trust database.
    /// The system trust is generated from the contents of the RPM database.
    /// This represents state in the current fapolicyd database, not necessarily
    /// matching what is currently in the RPM database.
    fn system_trust(&self) -> Vec<PyTrust> {
        self.state
            .trust_db
            .iter()
            .filter(|t| t.source == TrustSource::System)
            .map(trust_status)
            .flatten()
            .map(PyTrust::from)
            .collect()
    }

    fn system_trust_allow_threads(&self, py: Python) -> Vec<PyTrust> {
        py.allow_threads(|| self.system_trust())
    }

    /// Obtain a list of trusted files sourced from the ancillary trust database.
    /// This represents state in the current fapolicyd database, not necessarily
    /// matching what is currently in the ancillary trust file.
    fn ancillary_trust(&self) -> Vec<PyTrust> {
        self.state
            .trust_db
            .iter()
            .filter(|t| t.source == TrustSource::Ancillary)
            .map(trust_status)
            .flatten()
            .map(PyTrust::from)
            .collect()
    }

    /// Apply the changeset to the state of this System generating a new System
    fn apply_changeset(&self, change: PyChangeset) -> PySystem {
        self.state.apply_trust_changes(change.into()).into()
    }

    /// Update the host system with this state of this System
    fn deploy(&self) {
        deploy_app_state(&self.state).expect("deployment failed")
    }

    /// Check the host system state against the state of this System
    fn is_stale(&self) -> bool {
        // todo;; check current state againt rpm and file
        false
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySystem>()?;
    Ok(())
}
