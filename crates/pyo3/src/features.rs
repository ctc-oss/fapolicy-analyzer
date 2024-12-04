/*
 * Copyright Concurrent Technologies Corporation 2024
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use pyo3::prelude::*;

/// Indicates whether the audit capability is available on this platform
#[pyfunction]
fn is_audit_available() -> bool {
    cfg!(feature = "audit")
}

/// Indicates whether performance stats are is available on this platform
#[pyfunction]
fn is_stats_available() -> bool {
    cfg!(feature = "stats")
}

pub fn init_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_audit_available, m)?)?;
    m.add_function(wrap_pyfunction!(is_stats_available, m)?)?;
    Ok(())
}
