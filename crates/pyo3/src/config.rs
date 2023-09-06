/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;

use fapolicy_app::cfg;

/// Provide path to the application config file
#[pyfunction]
fn config_file_path() -> PyResult<String> {
    cfg::All::config_file()
        .map(|p| p.display().to_string())
        .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
}

/// log dir
/// xdg or /var/log/fapolicy-analyzer/
#[pyfunction]
fn app_log_dir() -> String {
    cfg::log_dir()
}

/// data dir (for autosave things)
/// xdg or /var/lib/fapolicy-analyzer/
#[pyfunction]
fn app_data_dir() -> String {
    cfg::data_dir()
}

/// config dir
/// xdg or /etc/fapolicy-analyzer/
#[pyfunction]
fn app_config_dir() -> String {
    cfg::config_dir()
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(config_file_path, m)?)?;
    m.add_function(wrap_pyfunction!(app_log_dir, m)?)?;
    m.add_function(wrap_pyfunction!(app_data_dir, m)?)?;
    m.add_function(wrap_pyfunction!(app_config_dir, m)?)?;
    Ok(())
}
