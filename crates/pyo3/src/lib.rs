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
pub mod daemon;
pub mod rules;
pub mod system;
pub mod trust;

#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    acl::init_module(_py, m)?;
    analysis::init_module(_py, m)?;
    daemon::init_module(_py, m)?;
    rules::init_module(_py, m)?;
    system::init_module(_py, m)?;
    trust::init_module(_py, m)?;
    Ok(())
}
