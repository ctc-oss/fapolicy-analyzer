use pyo3::prelude::*;
use pyo3::{exceptions, PyResult};

use fapolicy_analyzer::app::State;
use fapolicy_analyzer::cfg;
use fapolicy_analyzer::check::trust_status;
use fapolicy_analyzer::log::Event;
use fapolicy_analyzer::sys::deploy_app_state;

use crate::acl::{PyGroup, PyUser};
use crate::event::PyEvent;

use super::trust::PyChangeset;
use super::trust::PyTrust;

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
    /// Create a new initialized System
    /// This returns a result object that will be an error if initialization fails,
    /// allowing the member accessors on the System to return non-result objects.
    #[new]
    fn new() -> PyResult<PySystem> {
        let conf = cfg::All::load();
        match State::load(&conf) {
            Ok(state) => Ok(state.into()),
            Err(e) => Err(exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
        }
    }

    /// Obtain a list of trusted files sourced from the system trust database.
    /// The system trust is generated from the contents of the RPM database.
    /// This represents state in the current fapolicyd database, not necessarily
    /// matching what is currently in the RPM database.
    fn system_trust(&self) -> Vec<PyTrust> {
        self.state
            .trust_db
            .iter()
            .filter(|(_, m)| m.is_system())
            .map(|(_, m)| trust_status(&m.trusted))
            .flatten()
            .map(PyTrust::from)
            .collect()
    }

    /// Obtain a list of trusted files sourced from the system trust database.
    /// The system trust is generated from the contents of the RPM database.
    /// This represents state in the current fapolicyd database, not necessarily
    /// matching what is currently in the RPM database.
    /// This call will not block other threads from executing.
    fn system_trust_async(&self, py: Python) -> Vec<PyTrust> {
        py.allow_threads(|| self.system_trust())
    }

    /// Obtain a list of trusted files sourced from the ancillary trust database.
    /// This represents state in the current fapolicyd database, not necessarily
    /// matching what is currently in the ancillary trust file.
    fn ancillary_trust(&self) -> Vec<PyTrust> {
        self.state
            .trust_db
            .iter()
            .filter(|(_, m)| m.is_ancillary())
            .map(|(_, m)| trust_status(&m.trusted))
            .flatten()
            .map(PyTrust::from)
            .collect()
    }

    /// Obtain a list of trusted files sourced from the ancillary trust database.
    /// This represents state in the current fapolicyd database, not necessarily
    /// matching what is currently in the ancillary trust file.
    /// This call will not block other threads from executing.
    fn ancillary_trust_async(&self, py: Python) -> Vec<PyTrust> {
        py.allow_threads(|| self.ancillary_trust())
    }

    /// Apply the changeset to the state of this System generating a new System
    fn apply_changeset(&self, change: PyChangeset) -> PySystem {
        self.state.apply_trust_changes(change.into()).into()
    }

    /// Update the host system with this state of this System
    fn deploy(&self) -> PyResult<()> {
        match deploy_app_state(&self.state) {
            Ok(_) => Ok(()),
            Err(e) => Err(exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
        }
    }

    /// Check the host system state against the state of this System
    fn is_stale(&self) -> bool {
        // todo;; check current state againt rpm and file
        false
    }

    /// Load a list of system users
    fn users(&self) -> Vec<PyUser> {
        self.state.users.iter().map(|u| u.clone().into()).collect()
    }

    /// Load a list of system groups
    fn groups(&self) -> Vec<PyGroup> {
        self.state.groups.iter().map(|g| g.clone().into()).collect()
    }

    /// Parse all Events from the log at the specified path
    fn events_from(&self, log: &str) -> Vec<PyEvent> {
        let xs = Event::from_file(log);
        xs.iter().map(|e| PyEvent::from(e.clone())).collect()
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PySystem>()?;
    Ok(())
}
