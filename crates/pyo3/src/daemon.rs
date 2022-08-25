/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::system::PySystem;
use fapolicy_daemon::fapolicyd::Version;
use fapolicy_daemon::svc::State::{Active, Inactive};
use fapolicy_daemon::svc::{wait_for_daemon, Handle};
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

#[pyclass(module = "svc", name = "Handle")]
#[derive(Clone, Default)]
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

    /// returns the unit status, throws if invalid unit
    pub fn is_active(&self) -> PyResult<bool> {
        self.rs
            .active()
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
    }

    /// returns true if the unit exists, false otherwise
    pub fn is_valid(&self) -> bool {
        self.rs.active().is_ok()
    }

    #[args(timeout = 15)]
    pub fn wait_until_active(&self, timeout: usize) -> PyResult<()> {
        wait_for_daemon(&self.rs, Active, timeout)
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
    }

    #[args(timeout = 15)]
    pub fn wait_until_inactive(&self, timeout: usize) -> PyResult<()> {
        wait_for_daemon(&self.rs, Inactive, timeout)
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
    }
}

#[pyfunction]
fn start_fapolicyd() -> PyResult<()> {
    let d: PyHandle = Handle::default().into();
    d.start()
}

#[pyfunction]
fn stop_fapolicyd() -> PyResult<()> {
    let d: PyHandle = Handle::default().into();
    d.stop()
}

#[pyfunction]
fn fapolicyd_version() -> Option<String> {
    match fapolicy_daemon::version() {
        Version::Unknown => None,
        Version::Release {
            major,
            minor,
            patch,
        } => Some(format!("{}.{}.{}", major, minor, patch)),
    }
}

pub(crate) fn deploy(system: &PySystem) -> PyResult<()> {
    let handle = PyHandle::default();
    handle
        .stop()
        .and_then(|_| handle.wait_until_inactive(15))
        .and_then(|_| system.deploy_only())
        .and_then(|_| handle.start())
        .and_then(|_| handle.wait_until_active(15))
}

#[pyfunction]
fn rollback_fapolicyd(to: PySystem) -> PyResult<()> {
    deploy(&to)
}

#[pyfunction]
fn is_fapolicyd_active() -> PyResult<bool> {
    Handle::default()
        .active()
        .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyHandle>()?;
    m.add_function(wrap_pyfunction!(fapolicyd_version, m)?)?;
    m.add_function(wrap_pyfunction!(start_fapolicyd, m)?)?;
    m.add_function(wrap_pyfunction!(stop_fapolicyd, m)?)?;
    m.add_function(wrap_pyfunction!(rollback_fapolicyd, m)?)?;
    m.add_function(wrap_pyfunction!(is_fapolicyd_active, m)?)?;
    Ok(())
}
