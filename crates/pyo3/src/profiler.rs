/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use pyo3::prelude::*;
use pyo3::{exceptions, PyResult, Python};

use fapolicy_daemon::profiler::Profiler;

#[pyclass(module = "daemon", name = "Profiler")]
pub struct PyProfiler {
    rs: Profiler,
}
impl From<Profiler> for PyProfiler {
    fn from(rs: Profiler) -> Self {
        Self { rs }
    }
}
impl From<PyProfiler> for Profiler {
    fn from(py: PyProfiler) -> Self {
        py.rs
    }
}

#[pymethods]
impl PyProfiler {
    #[new]
    fn new() -> Self {
        Self {
            rs: Profiler::new(),
        }
    }

    fn activate(&self) -> PyResult<()> {
        self.activate()
            .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))
    }

    fn deactivate(&self) -> PyResult<()> {
        self.deactivate()
            .map_err(|e| exceptions::PyRuntimeError::new_err(format!("{:?}", e)))
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyProfiler>()?;
    Ok(())
}
