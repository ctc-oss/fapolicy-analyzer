/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use pyo3::prelude::*;

use fapolicy_analyzer::users::{Group, User};

/// Represents a host system user parsed from /etc/passwd
#[pyclass(module = "acl", name = "User")]
#[derive(Clone)]
pub struct PyUser {
    rs: User,
}
impl From<User> for PyUser {
    fn from(rs: User) -> Self {
        Self { rs }
    }
}
impl From<PyUser> for User {
    fn from(py: PyUser) -> Self {
        py.rs
    }
}

#[pymethods]
impl PyUser {
    /// The user id (UID) of the user
    #[getter]
    fn id(&self) -> u32 {
        self.rs.uid
    }

    /// The username of the user
    #[getter]
    fn name(&self) -> &str {
        &self.rs.name
    }

    /// The primary group id (GID) of the user
    #[getter]
    fn primary_group_id(&self) -> u32 {
        self.rs.gid
    }
}

/// Represents a host system group parsed from /etc/group
#[pyclass(module = "acl", name = "Group")]
#[derive(Clone)]
pub struct PyGroup {
    rs: Group,
}

impl From<Group> for PyGroup {
    fn from(rs: Group) -> Self {
        Self { rs }
    }
}
impl From<PyGroup> for Group {
    fn from(py: PyGroup) -> Self {
        py.rs
    }
}

#[pymethods]
impl PyGroup {
    /// The group id (GID) of the group
    #[getter]
    fn id(&self) -> u32 {
        self.rs.gid
    }

    /// The name of the group
    #[getter]
    fn name(&self) -> String {
        self.rs.name.clone()
    }

    /// List of member UIDs that are members of this group
    #[getter]
    fn members(&self) -> Vec<String> {
        self.rs.users.clone()
    }
}

pub fn init_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyUser>()?;
    m.add_class::<PyGroup>()?;
    Ok(())
}
