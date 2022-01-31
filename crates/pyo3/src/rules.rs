/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use pyo3::prelude::*;

#[pyclass(module = "rules", name = "Rule")]
#[derive(Clone)]
pub struct PyRule {
    pub id: usize,
    pub text: String,
}

impl PyRule {
    pub fn new(id: usize, text: String) -> Self {
        Self { id, text }
    }
}

#[pymethods]
impl PyRule {
    #[getter]
    fn get_id(&self) -> usize {
        self.id
    }

    #[getter]
    fn get_text(&self) -> String {
        self.text.clone()
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyRule>()?;
    Ok(())
}
