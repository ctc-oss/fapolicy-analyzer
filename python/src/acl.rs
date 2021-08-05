use fapolicy_analyzer::users::{Group, User};
use pyo3::prelude::*;

/// Represents a host system user parsed from /etc/passwd
#[pyclass(module = "acl", name = "User")]
#[derive(Clone)]
pub struct PyUser {
    user: User,
}
impl From<User> for PyUser {
    fn from(user: User) -> Self {
        Self { user }
    }
}
impl From<PyUser> for User {
    fn from(user: PyUser) -> Self {
        user.user
    }
}

#[pymethods]
impl PyUser {
    /// The user id (UID) of the user
    #[getter]
    fn id(&self) -> u32 {
        self.user.uid
    }
    #[getter]

    /// The username of the user
    fn name(&self) -> &str {
        &self.user.name
    }

    /// The primary group id (GID) of the user
    #[getter]
    fn primary_group_id(&self) -> u32 {
        self.user.gid
    }
}

/// Represents a host system group parsed from /etc/group
#[pyclass(module = "acl", name = "Group")]
#[derive(Clone)]
pub struct PyGroup {
    group: Group,
}

impl From<Group> for PyGroup {
    fn from(group: Group) -> Self {
        Self { group }
    }
}
impl From<PyGroup> for Group {
    fn from(group: PyGroup) -> Self {
        group.group
    }
}

#[pymethods]
impl PyGroup {
    /// The group id (GID) of the group
    #[getter]
    fn id(&self) -> u32 {
        self.group.gid
    }

    /// The name of the group
    #[getter]
    fn name(&self) -> String {
        self.group.name.clone()
    }

    /// List of member UIDs that are members of this group
    #[getter]
    fn members(&self) -> Vec<String> {
        self.group.users.clone()
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyUser>()?;
    m.add_class::<PyGroup>()?;
    Ok(())
}
