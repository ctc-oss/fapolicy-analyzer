/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use fapolicy_rules::db::{RuleDef, DB};


use pyo3::exceptions::PyException;
use pyo3::prelude::*;

use pyo3::{create_exception, PyObjectProtocol, PyTypeInfo};

use fapolicy_rules::ops::Changeset;
use fapolicy_rules::parser::parse::StrTrace;
use fapolicy_rules::parser::rule::{parse_with_error_message};


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
    pub(crate) fn new(
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

#[pyproto]
impl PyObjectProtocol for PyRule {
    fn __str__(&self) -> PyResult<String> {
        Ok(format!("{}: {}", self.id, self.text))
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{}: {}", self.id, self.text))
    }
}

create_exception!(rust, InvalidRuleSyntax, PyException);

#[pymethods]
impl PyRule {
    #[new]
    fn py_new(id: usize, txt: &str) -> PyResult<PyRule> {
        match parse_with_error_message(StrTrace::new(txt)) {
            Ok(_r) => PyResult::Ok(PyRule {
                id,
                text: txt.to_string(),
                origin: "".to_string(),
                info: vec![],
                valid: true,
            }),
            Err(e) => Err(InvalidRuleSyntax::new_err(format!("{:?}", e))),
        }
    }

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

/// A mutable collection of rule changes
#[pyclass(module = "rules", name = "RuleChangeset")]
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

    pub fn rule(&self, id: usize) -> Option<PyRule> {
        self.rs.rule(id).map(|d| PyRule {
            id,
            text: d.to_string(),
            origin: "".to_string(),
            info: vec![],
            valid: false,
        })
    }

    pub fn set(&mut self, text: String) -> bool {
        match self.rs.set(&text) {
            Ok(_) => true,
            Err(_) => false,
        }
    }
}

#[pyfunction]
fn rule_text_error_check(txt: &str) -> Option<String> {
    match parse_with_error_message(StrTrace::new(txt)) {
        Ok(_) => None,
        Err(s) => Some(s),
    }
}

pub(crate) fn db_to_vec(db: &DB) -> PyResult<Vec<PyRule>> {
    Ok(db
        .iter()
        .map(|(id, r)| {
            let (valid, text, info) = match r {
                RuleDef::Invalid { text, error } => {
                    (false, text.clone(), vec![("e".to_string(), error.clone())])
                }
                RuleDef::Valid(r) => (true, r.to_string(), vec![]),
                RuleDef::ValidWithWarning(r, w) => {
                    (true, r.to_string(), vec![("w".to_string(), w.clone())])
                }
            };
            let origin = db
                .source(*id)
                // todo;; this should be converted to a python exception
                .unwrap_or_else(|| "<unknown>".to_string());

            PyRule::new(*id, text, origin, info, valid)
        })
        .collect())
}

// #[pyfunction]
// fn text_to_rule_db(txt: &str) -> PyResult<PyDict> {}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyRule>()?;
    m.add_class::<PyRuleInfo>()?;
    m.add_class::<PyChangeset>()?;
    m.add_function(wrap_pyfunction!(rule_text_error_check, m)?)?;
    Ok(())
}
