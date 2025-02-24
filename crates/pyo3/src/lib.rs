/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use pyo3::prelude::*;

pub mod acl;
pub mod analysis;
pub mod check;
pub mod config;
pub mod daemon;
pub mod features;
pub mod profiler;
pub mod rules;
pub mod system;
pub mod trust;

#[pymodule]
fn rust(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    acl::init_module(_py, m)?;
    analysis::init_module(_py, m)?;
    check::init_module(_py, m)?;
    config::init_module(_py, m)?;
    daemon::init_module(_py, m)?;
    features::init_module(_py, m)?;
    profiler::init_module(_py, m)?;
    rules::init_module(_py, m)?;
    system::init_module(_py, m)?;
    trust::init_module(_py, m)?;
    m.add_function(wrap_pyfunction!(init_native_logging, m)?)?;
    Ok(())
}

#[pyfunction]
fn init_native_logging() {
    pyo3_log::init();
}
