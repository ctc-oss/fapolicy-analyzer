/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use pyo3::prelude::*;
use pyo3::{exceptions, PyObjectProtocol};

use fapolicy_rules::db::Entry::*;
use fapolicy_rules::db::DB;
use fapolicy_rules::error::Error::MalformedFileMarker;
use fapolicy_rules::ops::Changeset;
use fapolicy_rules::parser::parse::StrTrace;
use fapolicy_rules::parser::rule::parse_with_error_message;

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

#[pyproto]
impl PyObjectProtocol for PyRule {
    fn __str__(&self) -> PyResult<String> {
        Ok(format!("{}: {}", self.id, self.text))
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{}: {}", self.id, self.text))
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

    pub fn get(&self) -> Vec<PyRule> {
        self.rules()
    }

    pub fn rules(&self) -> Vec<PyRule> {
        rules_to_vec(self.rs.get())
    }

    pub fn set(&mut self, text: &str) -> bool {
        self.rs.set(&text.trim()).is_ok()
    }

    pub fn parse(&mut self, text: &str) -> PyResult<()> {
        match self.rs.set(&text.trim()) {
            Ok(_) => Ok(()),
            Err(MalformedFileMarker(lnum, txt)) => Err(exceptions::PyRuntimeError::new_err(
                format!("{}:malformed-file-marker:{}", lnum, txt),
            )),
            Err(e) => Err(exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
        }
    }

    pub fn text(&self) -> Option<&str> {
        self.rs.src().map(|s| &**s)
    }
}

#[pyfunction]
fn rule_text_error_check(txt: &str) -> Option<String> {
    match parse_with_error_message(StrTrace::new(txt)) {
        Ok(_) => None,
        Err(s) => Some(s),
    }
}

pub(crate) fn rules_to_vec(db: &DB) -> Vec<PyRule> {
    db.rules()
        .iter()
        .map(|e| {
            let (valid, text, info) = if e.valid {
                if e.msg.is_some() {
                    let w = e.msg.as_ref().unwrap();
                    (true, e.text.clone(), vec![("w".to_string(), w.clone())])
                } else {
                    (true, e.text.clone(), vec![])
                }
            } else {
                let err = e.msg.as_deref().unwrap_or("???");
                (
                    false,
                    e.text.clone(),
                    vec![("e".to_string(), err.to_string())],
                )
            };
            PyRule::new(e.id, text, e.origin.clone(), info, valid)
        })
        .collect()
}

pub(crate) fn entries_to_vec(db: &DB) -> Vec<PyRule> {
    db.iter()
        .map(|(id, (origin, e))| {
            let (valid, text, info) = match e {
                Invalid { text, error } => {
                    (false, text.clone(), vec![("e".to_string(), error.clone())])
                }
                InvalidSet { text, error } => {
                    (false, text.clone(), vec![("e".to_string(), error.clone())])
                }
                ValidRule(r) => (true, r.to_string(), vec![]),
                ValidSet(s) => (true, s.to_string(), vec![]),
                RuleWithWarning(r, w) => (true, r.to_string(), vec![("w".to_string(), w.clone())]),
                SetWithWarning(r, w) => (true, r.to_string(), vec![("w".to_string(), w.clone())]),
            };
            PyRule::new(*id, text, origin.to_string(), info, valid)
        })
        .collect()
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
