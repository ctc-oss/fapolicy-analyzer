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

/// Provide path to the application config file
#[pyfunction]
fn set_config_file_path(p: String) -> String {
   let config_file_path_msg = String::from("Loading config from: ") + &p;
   return config_file_path_msg;
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(config_file_path, m)?)?;
    m.add_function(wrap_pyfunction!(set_config_file_path, m)?)?;
    Ok(())
}
