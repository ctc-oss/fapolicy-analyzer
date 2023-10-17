/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::system::PySystem;
use fapolicy_daemon::conf;
use fapolicy_daemon::conf::ops::Changeset;
use fapolicy_daemon::conf::{with_error_message, Line};
use fapolicy_daemon::fapolicyd::Version;
use fapolicy_daemon::svc::State::{Active, Inactive};
use fapolicy_daemon::svc::{wait_for_service, Handle};
use pyo3::exceptions;
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

    /// returns true if the unit is valid, false otherwise
    pub fn is_valid(&self) -> bool {
        self.rs.valid().unwrap_or(false)
    }

    #[args(timeout = 15)]
    pub fn wait_until_active(&self, timeout: usize) -> PyResult<()> {
        wait_for_service(&self.rs, Active, timeout)
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
    }

    #[args(timeout = 15)]
    pub fn wait_until_inactive(&self, timeout: usize) -> PyResult<()> {
        wait_for_service(&self.rs, Inactive, timeout)
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

pub(crate) fn conf_to_text(db: &conf::DB) -> String {
    db.iter()
        .fold(String::new(), |acc, line| format!("{acc}\n{line}"))
        .trim_start()
        .to_owned()
}

pub(crate) fn conf_to_error_text(db: &conf::DB) -> String {
    db.iter()
        .fold(String::new(), |acc, line| match line {
            Line::Invalid { k, v } => format!("{acc}\nInvalid: {k}={v}"),
            Line::Malformed(s) => format!("{acc}\nMalformed: {s}"),
            Line::Duplicate(s) => format!("{acc}\nDuplicated: {s}"),
            _ => acc,
        })
        .trim_start()
        .to_owned()
}

/// A mutable collection of rule changes
#[pyclass(module = "daemon", name = "ConfigChangeset")]
#[derive(Default, Clone)]
pub struct PyChangeset {
    rs: Changeset,
}

impl From<Changeset> for PyChangeset {
    fn from(rs: Changeset) -> Self {
        Self { rs }
    }
}

impl From<PyChangeset> for Changeset {
    fn from(py: PyChangeset) -> Self {
        py.rs
    }
}

#[pymethods]
impl PyChangeset {
    #[new]
    pub fn new() -> Self {
        PyChangeset::default()
    }

    pub fn parse(&mut self, text: &str) -> PyResult<()> {
        match self.rs.set(text.trim()) {
            Ok(_) => Ok(()),
            Err(e) => Err(exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
        }
    }

    pub fn text(&self) -> Option<&str> {
        self.rs.src().map(|s| &**s)
    }
}

#[pyfunction]
fn conf_text_error_check(txt: &str) -> Option<String> {
    match with_error_message(txt) {
        Ok(_) => None,
        Err(s) => Some(s),
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyHandle>()?;
    m.add_class::<PyChangeset>()?;
    m.add_function(wrap_pyfunction!(fapolicyd_version, m)?)?;
    m.add_function(wrap_pyfunction!(start_fapolicyd, m)?)?;
    m.add_function(wrap_pyfunction!(stop_fapolicyd, m)?)?;
    m.add_function(wrap_pyfunction!(rollback_fapolicyd, m)?)?;
    m.add_function(wrap_pyfunction!(is_fapolicyd_active, m)?)?;
    m.add_function(wrap_pyfunction!(conf_text_error_check, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use crate::daemon::{conf_to_error_text, conf_to_text};
    use fapolicy_daemon::conf::config::ConfigToken::{DoStatReport, Permissive};
    use fapolicy_daemon::conf::Line::*;
    use fapolicy_daemon::conf::DB;

    #[test]
    fn test_conf_to_text_blank_lines() {
        let f: DB = vec![BlankLine].into();
        assert_eq!(conf_to_text(&f), "".to_string());

        let f: DB = vec![Comment("foo".to_string()), BlankLine].into();
        assert_eq!(conf_to_text(&f), "foo\n".to_string());
    }

    #[test]
    fn test_conf_to_text_malformed_single() {
        let f: DB = vec![Malformed("Foo".to_string())].into();
        assert_eq!(conf_to_text(&f), "Foo".to_string())
    }

    #[test]
    fn test_conf_to_text_malformed_multi() {
        let s = "Foo".to_string();
        let f: DB = vec![Malformed(s.clone()), Malformed(s)].into();
        assert_eq!(conf_to_text(&f), "Foo\nFoo".to_string())
    }

    #[test]
    fn test_conf_to_text_valid_multi() {
        let a = Valid(Permissive(true));
        let b = Valid(DoStatReport(false));
        let f: DB = vec![a, b].into();
        assert_eq!(
            conf_to_text(&f),
            "permissive = 1\ndo_stat_report = 0".to_string()
        )
    }

    #[test]
    fn test_conf_to_error_text_empty() {
        let b = BlankLine;
        let c = Comment("Foo".to_owned());
        let v = Valid(DoStatReport(false));
        let f: DB = vec![b, c, v].into();
        assert_eq!(conf_to_error_text(&f), "".to_string())
    }

    #[test]
    fn test_conf_to_error_text_invalid() {
        let a = Invalid {
            k: "x".to_owned(),
            v: "y".to_owned(),
        };
        let f: DB = vec![a].into();
        assert_eq!(conf_to_error_text(&f), "Invalid: x=y".to_string())
    }

    #[test]
    fn test_conf_to_error_text_malformed() {
        let a = Malformed("googlygak".to_owned());
        let f: DB = vec![a].into();
        assert_eq!(conf_to_error_text(&f), "Malformed: googlygak".to_string())
    }

    #[test]
    fn test_conf_to_error_text_duplicated() {
        let a = Duplicate(Permissive(true));
        let f: DB = vec![a].into();
        assert_eq!(
            conf_to_error_text(&f),
            "Duplicated: permissive = 1".to_string()
        )
    }

    #[test]
    fn test_conf_to_error_text_mixed() {
        let a = Invalid {
            k: "x".to_owned(),
            v: "y".to_owned(),
        };
        let b = Malformed("googlygak".to_owned());
        let f: DB = vec![a, b].into();
        assert_eq!(
            conf_to_error_text(&f),
            "Invalid: x=y\nMalformed: googlygak".to_string()
        )
    }
}
