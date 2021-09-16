use pyo3::prelude::*;

use fapolicy_analyzer::log::Event;
use fapolicy_analyzer::rules::ObjPart;
use fapolicy_analyzer::rules::SubjPart;

/// An Event parsed from a fapolicyd log
#[pyclass(module = "log", name = "Event")]
#[derive(Clone)]
pub struct PyEvent {
    event: Event,
}
impl From<Event> for PyEvent {
    fn from(event: Event) -> Self {
        Self { event }
    }
}
impl From<PyEvent> for Event {
    fn from(event: PyEvent) -> Self {
        event.event
    }
}

#[pymethods]
impl PyEvent {
    /// The user id parsed from the log event
    #[getter]
    fn uid(&self) -> i32 {
        self.event.uid
    }

    /// The group id parsed from the log event
    #[getter]
    fn gid(&self) -> i32 {
        self.event.gid
    }

    /// The fapolicyd subject parsed from the log event
    #[getter]
    fn subject(&self) -> PySubject {
        let path = if let Some(SubjPart::Exe(path)) = self
            .event
            .subj
            .parts
            .iter()
            .find(|p| matches!(p, SubjPart::Exe(_)))
        {
            path.clone()
        } else {
            "invalid".into()
        };

        PySubject {
            file: path,
            trust: "ST".to_string(),
            access: "A".to_string(),
        }
    }

    /// The fapolicyd object parsed from the log event
    #[getter]
    fn object(&self) -> PyObject {
        let path = if let Some(ObjPart::Path(path)) = self
            .event
            .obj
            .parts
            .iter()
            .find(|p| matches!(p, ObjPart::Path(_)))
        {
            path.clone()
        } else {
            "invalid".into()
        };

        PyObject {
            file: path,
            trust: "ST".into(),
            access: "A".into(),
            mode: "R".into(),
        }
    }
}

/// Subject metadata
#[pyclass(module = "log", name = "Subject")]
#[derive(Clone)]
pub struct PySubject {
    file: String,
    trust: String,
    access: String,
}

/// Object metadata
#[pyclass(module = "log", name = "Object")]
#[derive(Clone)]
pub struct PyObject {
    file: String,
    trust: String,
    access: String,
    mode: String,
}

#[pymethods]
impl PySubject {
    /// Path of the subject parsed from the log event
    #[getter]
    fn file(&self) -> String {
        self.file.clone()
    }

    /// Trust status of the log event subject
    #[getter]
    fn trust(&self) -> String {
        self.trust.clone()
    }

    /// Access status of the log event subject
    #[getter]
    fn access(&self) -> String {
        self.access.clone()
    }
}

#[pymethods]
impl PyObject {
    /// Path of the object parsed from the log event
    #[getter]
    fn file(&self) -> String {
        self.file.clone()
    }

    /// Trust status of the log event object
    #[getter]
    fn trust(&self) -> String {
        self.trust.clone()
    }

    /// Access status of the log event object
    #[getter]
    fn access(&self) -> String {
        self.access.clone()
    }

    /// Mode of the log event object
    #[getter]
    fn mode(&self) -> String {
        self.mode.clone()
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyEvent>()?;
    m.add_class::<PySubject>()?;
    m.add_class::<PyObject>()?;
    Ok(())
}
