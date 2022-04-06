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
    pub origin: String,
    pub info: Vec<PyRuleInfo>,
    pub valid: bool,
}

impl PyRule {
    pub fn new(
        id: usize,
        text: String,
        origin: String,
        info: Vec<(String, String)>,
        valid: bool,
    ) -> Self {
        let info = info
            .iter()
            .map(|(c, m)| PyRuleInfo {
                category: c.clone(),
                message: m.clone(),
            })
            .collect();

        Self {
            id,
            text,
            origin,
            info,
            valid,
        }
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

    #[getter]
    fn get_origin(&self) -> String {
        self.origin.clone()
    }

    #[getter]
    fn get_info(&self) -> Vec<PyRuleInfo> {
        self.info.clone()
    }

    #[getter]
    fn is_valid(&self) -> bool {
        self.valid
    }
}

#[pyclass(module = "rules", name = "Info")]
#[derive(Clone)]
pub struct PyRuleInfo {
    pub category: String,
    pub message: String,
}

#[pymethods]
impl PyRuleInfo {
    #[getter]
    fn get_category(&self) -> String {
        self.category.clone()
    }

    #[getter]
    fn get_message(&self) -> String {
        self.message.clone()
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyRule>()?;
    m.add_class::<PyRuleInfo>()?;
    Ok(())
}
