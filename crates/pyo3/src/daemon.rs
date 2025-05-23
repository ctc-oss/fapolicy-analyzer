/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */
use crate::system::PySystem;
use fapolicy_daemon::conf::ops::Changeset;
use fapolicy_daemon::conf::{with_error_message, Line};
use fapolicy_daemon::fapolicyd::Version;
use fapolicy_daemon::stats::{Rec, RecTs};
use fapolicy_daemon::svc::State::{Active, Inactive};
use fapolicy_daemon::svc::{wait_for_service, Handle};
use fapolicy_daemon::{conf, pipe, stats};
use pyo3::exceptions;
use pyo3::exceptions::PyRuntimeError;
use pyo3::indoc::indoc;
use pyo3::prelude::*;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;

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

    #[pyo3(signature = (timeout = 15))]
    pub fn wait_until_active(&self, timeout: usize) -> PyResult<()> {
        wait_for_service(&self.rs, Active, timeout)
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
    }

    #[pyo3(signature = (timeout = 15))]
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

#[pyclass(module = "daemon", name = "ConfigInfo")]
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct PyConfigInfo {
    pub category: String,
    pub message: String,
}

#[pymethods]
impl PyConfigInfo {
    #[getter]
    fn get_category(&self) -> String {
        self.category.clone()
    }

    #[getter]
    fn get_message(&self) -> String {
        self.message.clone()
    }
}

pub(crate) fn conf_info(db: &conf::DB) -> Vec<PyConfigInfo> {
    let e = "e";
    db.iter().fold(vec![], |mut acc, line| {
        let message = match line {
            Line::Invalid { k, v } => Some(format!("Invalid: {k}={v}")),
            Line::Malformed(s) => Some(format!("Malformed: {s}")),
            Line::Duplicate(s) => Some(format!("Duplicated: {s}")),
            _ => None,
        };
        if let Some(message) = message {
            acc.push(PyConfigInfo {
                category: e.to_owned(),
                message,
            });
        };
        acc
    })
}

/// A mutable collection of config changes
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

    fn parse(&mut self, text: &str) -> PyResult<()> {
        match self.rs.set(text.trim()) {
            Ok(_) => Ok(()),
            Err(e) => Err(exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
        }
    }

    fn text(&self) -> Option<&str> {
        self.rs.src().map(|s| &**s)
    }

    fn config_info(&self) -> Vec<PyConfigInfo> {
        conf_info(self.rs.get())
    }

    fn is_valid(&self) -> bool {
        self.rs.get().is_valid()
    }
}

#[pyfunction]
fn conf_text_error_check(txt: &str) -> Option<String> {
    match with_error_message(txt) {
        Ok(_) => None,
        Err(s) => Some(s),
    }
}

#[pyclass(module = "stats", name = "StatStream")]
pub struct PyStatStream {
    kill_flag: Arc<AtomicBool>,
}

impl PyStatStream {
    pub fn kill(&self) {
        self.kill_flag.store(true, Ordering::Relaxed)
    }
}

#[pyclass(module = "stats", name = "Rec")]
pub struct PyRec {
    rs: Rec,
}

#[pymethods]
impl PyRec {
    fn q_size(&self) -> i32 {
        self.rs.q_size
    }
    fn inter_thread_max_queue_depth(&self) -> i32 {
        self.rs.inter_thread_max_queue_depth
    }
    fn allowed_accesses(&self) -> i32 {
        self.rs.allowed_accesses
    }
    fn denied_accesses(&self) -> i32 {
        self.rs.denied_accesses
    }
    fn trust_db_max_pages(&self) -> i32 {
        self.rs.trust_db_max_pages
    }
    fn trust_db_pages_in_use(&self) -> i32 {
        self.rs.trust_db_pages_in_use.0
    }
    fn trust_db_pages_in_use_pct(&self) -> f32 {
        self.rs.trust_db_pages_in_use.1
    }
    fn subject_cache_size(&self) -> i32 {
        self.rs.subject_cache_size
    }
    fn subject_slots_in_use(&self) -> i32 {
        self.rs.subject_slots_in_use.0
    }
    fn subject_slots_in_use_pct(&self) -> f32 {
        self.rs.subject_slots_in_use.1
    }
    fn object_hits(&self) -> i32 {
        self.rs.object_hits
    }

    fn summary(&self) -> String {
        format!(
            indoc!(
                "q_size: {}
                Inter-thread max queue depth: {}
                Allowed accesses: {}
                Denied accesses: {}
                Trust database max pages: {}
                Trust database pages in use: {} ({}%)
                Subject cache size: {}
                Subject slots in use: {} ({}%)
                Subject hits: {}
                Subject misses: {}
                Subject evictions: {} ({}%)
                Object cache size: {}
                Object slots in use: {} ({}%)
                Object hits: {}
                Object misses: {}
                Object evictions: {} ({}%)"
            ),
            self.rs.q_size,
            self.rs.inter_thread_max_queue_depth,
            self.rs.allowed_accesses,
            self.rs.denied_accesses,
            self.rs.trust_db_max_pages,
            self.rs.trust_db_pages_in_use.0,
            self.rs.trust_db_pages_in_use.1,
            self.rs.subject_cache_size,
            self.rs.subject_slots_in_use.0,
            self.rs.subject_slots_in_use.1,
            self.rs.subject_hits,
            self.rs.subject_misses,
            self.rs.subject_evictions.0,
            self.rs.subject_evictions.1,
            self.rs.object_cache_size,
            self.rs.object_slots_in_use.0,
            self.rs.object_slots_in_use.1,
            self.rs.object_hits,
            self.rs.object_misses,
            self.rs.object_evictions.0,
            self.rs.object_evictions.1,
        )
    }
}

#[pyclass(module = "stats", name = "RecTs")]
pub struct PyRecTs {
    rs: RecTs,
}

#[pymethods]
impl PyRecTs {
    fn timestamps(&self) -> Vec<i64> {
        self.rs.timestamps.clone()
    }
    fn allowed_accesses(&self) -> Vec<i32> {
        self.rs.allowed_accesses.clone()
    }
    fn denied_accesses(&self) -> Vec<i32> {
        self.rs.denied_accesses.clone()
    }
    fn trust_db_pages_in_use(&self) -> Vec<i32> {
        self.rs.trust_db_pages_in_use.clone()
    }
    fn subject_cache_size(&self) -> Vec<i32> {
        self.rs.subject_cache_size.clone()
    }
    fn subject_slots_in_use(&self) -> Vec<i32> {
        self.rs.subject_slots_in_use.clone()
    }
    fn object_hits(&self) -> Vec<i32> {
        self.rs.object_hits.clone()
    }

    fn subject_hits(&self) -> Vec<i32> {
        self.rs.subject_hits.clone()
    }
    fn subject_misses(&self) -> Vec<i32> {
        self.rs.subject_misses.clone()
    }
    fn subject_evictions(&self) -> Vec<i32> {
        self.rs.subject_evictions.clone()
    }
    fn object_cache_size(&self) -> Vec<i32> {
        self.rs.object_cache_size.clone()
    }
    fn object_slots_in_use(&self) -> Vec<i32> {
        self.rs.object_slots_in_use.clone()
    }
    fn object_misses(&self) -> Vec<i32> {
        self.rs.object_misses.clone()
    }
    fn object_evictions(&self) -> Vec<i32> {
        self.rs.object_evictions.clone()
    }
}

#[pyfunction]
fn start_stat_stream(path: &str, f: PyObject) -> PyResult<PyStatStream> {
    let kill_flag = Arc::new(AtomicBool::new(false));
    let rx = stats::read(path, kill_flag.clone()).expect("failed to read stats");

    thread::spawn(move || {
        for (rec, ts) in rx.iter() {
            Python::with_gil(|py| {
                if f.call1(py, ((PyRec { rs: rec }, PyRecTs { rs: ts }),))
                    .is_err()
                {
                    log::warn!("'tick' callback failed");
                }
            });
        }
    });

    Ok(PyStatStream { kill_flag })
}

/// send signal to fapolicyd FIFO pipe to reload the trust database
#[pyfunction]
fn signal_flush_cache() -> PyResult<()> {
    pipe::flush_cache()
        .map_err(|e| PyRuntimeError::new_err(format!("failed to signal cache flush: {:?}", e)))
}

pub fn init_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyHandle>()?;
    m.add_class::<PyChangeset>()?;
    m.add_class::<PyConfigInfo>()?;
    m.add_class::<PyRec>()?;
    m.add_class::<PyRecTs>()?;
    m.add_class::<PyStatStream>()?;
    m.add_function(wrap_pyfunction!(fapolicyd_version, m)?)?;
    m.add_function(wrap_pyfunction!(start_fapolicyd, m)?)?;
    m.add_function(wrap_pyfunction!(stop_fapolicyd, m)?)?;
    m.add_function(wrap_pyfunction!(rollback_fapolicyd, m)?)?;
    m.add_function(wrap_pyfunction!(is_fapolicyd_active, m)?)?;
    m.add_function(wrap_pyfunction!(conf_text_error_check, m)?)?;
    m.add_function(wrap_pyfunction!(start_stat_stream, m)?)?;
    m.add_function(wrap_pyfunction!(signal_flush_cache, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use crate::daemon::{conf_info, conf_to_text, PyConfigInfo};
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
        assert_eq!(conf_info(&f), vec![])
    }

    #[test]
    fn test_conf_to_error_text_invalid() {
        let a = Invalid {
            k: "x".to_owned(),
            v: "y".to_owned(),
        };
        let f: DB = vec![a].into();
        assert_eq!(
            conf_info(&f),
            vec![PyConfigInfo {
                category: "e".to_owned(),
                message: "Invalid: x=y".to_owned(),
            }]
        )
    }

    #[test]
    fn test_conf_to_error_text_malformed() {
        let a = Malformed("googlygak".to_owned());
        let f: DB = vec![a].into();
        assert_eq!(
            conf_info(&f),
            vec![PyConfigInfo {
                category: "e".to_owned(),
                message: "Malformed: googlygak".to_owned(),
            }]
        )
    }

    #[test]
    fn test_conf_to_error_text_duplicated() {
        let a = Duplicate(Permissive(true));
        let f: DB = vec![a].into();
        assert_eq!(
            conf_info(&f),
            vec![PyConfigInfo {
                category: "e".to_string(),
                message: "Duplicated: permissive = 1".to_string(),
            }]
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
            conf_info(&f),
            vec![
                PyConfigInfo {
                    category: "e".to_string(),
                    message: "Invalid: x=y".to_string(),
                },
                PyConfigInfo {
                    category: "e".to_string(),
                    message: "Malformed: googlygak".to_string(),
                }
            ]
        )
    }
}
