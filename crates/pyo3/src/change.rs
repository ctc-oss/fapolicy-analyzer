use std::collections::HashMap;

use pyo3::prelude::*;

use fapolicy_trust::ops::{get_path_action_map, Changeset};

/// A mutable collection of changes
#[pyclass(module = "trust", name = "Changeset")]
#[derive(Clone)]
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

impl Default for PyChangeset {
    fn default() -> Self {
        Changeset::new().into()
    }
}

#[pymethods]
impl PyChangeset {
    #[new]
    pub fn new() -> Self {
        PyChangeset::default()
    }

    pub fn add_trust(&mut self, path: &str) {
        self.rs.add(path)
    }

    pub fn del_trust(&mut self, path: &str) {
        self.rs.del(path)
    }

    pub fn len(&self) -> usize {
        self.rs.len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn get_path_action_map(&self) -> HashMap<String, String> {
        get_path_action_map(&self.rs)
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyChangeset>()?;
    Ok(())
}
