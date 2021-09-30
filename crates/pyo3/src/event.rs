use pyo3::prelude::*;

use fapolicy_analyzer::event::{Analysis, ObjAnalysis, SubjAnalysis};

/// An Event parsed from a fapolicyd log
#[pyclass(module = "log", name = "Event")]
#[derive(Clone)]
pub struct PyEvent {
    rs: Analysis,
}
impl From<Analysis> for PyEvent {
    fn from(rs: Analysis) -> Self {
        Self { rs }
    }
}
impl From<PyEvent> for Analysis {
    fn from(py: PyEvent) -> Self {
        py.rs
    }
}

#[pymethods]
impl PyEvent {
    /// The user id parsed from the log event
    #[getter]
    fn uid(&self) -> i32 {
        self.rs.event.uid
    }

    /// The group id parsed from the log event
    #[getter]
    fn gid(&self) -> i32 {
        // todo;; unhack this
        *self.rs.event.gid.iter().nth(0).unwrap()
    }

    /// The fapolicyd subject parsed from the log event
    #[getter]
    fn subject(&self) -> PySubject {
        self.rs.subject.clone().into()
    }

    /// The fapolicyd object parsed from the log event
    #[getter]
    fn object(&self) -> PyObject {
        self.rs.object.clone().into()
    }
}

/// Subject metadata
#[pyclass(module = "log", name = "Subject")]
#[derive(Clone)]
pub struct PySubject {
    rs: SubjAnalysis,
}

impl From<SubjAnalysis> for PySubject {
    fn from(rs: SubjAnalysis) -> Self {
        Self { rs }
    }
}
impl From<PySubject> for SubjAnalysis {
    fn from(py: PySubject) -> Self {
        py.rs
    }
}

#[pymethods]
impl PySubject {
    /// Path of the subject parsed from the log event
    #[getter]
    fn file(&self) -> String {
        self.rs.file.clone()
    }

    /// Trust status of the log event subject
    #[getter]
    fn trust(&self) -> String {
        self.rs.trust.clone()
    }

    /// Access status of the log event subject
    #[getter]
    fn access(&self) -> String {
        self.rs.access.clone()
    }
}

/// Object metadata
#[pyclass(module = "log", name = "Object")]
#[derive(Clone)]
pub struct PyObject {
    rs: ObjAnalysis,
}

impl From<ObjAnalysis> for PyObject {
    fn from(rs: ObjAnalysis) -> Self {
        Self { rs }
    }
}
impl From<PyObject> for ObjAnalysis {
    fn from(py: PyObject) -> Self {
        py.rs
    }
}

#[pymethods]
impl PyObject {
    /// Path of the object parsed from the log event
    #[getter]
    fn file(&self) -> String {
        self.rs.file.clone()
    }

    /// Trust status of the log event object
    #[getter]
    fn trust(&self) -> String {
        self.rs.trust.clone()
    }

    /// Access status of the log event object
    #[getter]
    fn access(&self) -> String {
        self.rs.access.clone()
    }

    /// Mode of the log event object
    #[getter]
    fn mode(&self) -> String {
        self.rs.mode.clone()
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyEvent>()?;
    m.add_class::<PySubject>()?;
    m.add_class::<PyObject>()?;
    Ok(())
}
