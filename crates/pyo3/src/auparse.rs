/*
 * Copyright Concurrent Technologies Corporation 2023
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

#[cfg(feature = "audit")]
#[pyfunction]
fn parse_audit_log(path: String) -> Vec<String> {
    use fapolicy_analyzer::events;
    events::read::from_auditlog_file(&path)
        .expect("parse_audit_log pyo3")
        .into_iter()
        .map(|e| format!("{e:?}"))
        .collect()
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_audit_available, m)?)?;
    #[cfg(feature = "audit")]
    m.add_function(wrap_pyfunction!(parse_audit_log, m)?)?;
    Ok(())
}
