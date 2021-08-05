use fapolicy_analyzer::log::Event;
use fapolicy_analyzer::rules::ObjPart;
use fapolicy_analyzer::rules::SubjPart;
use pyo3::prelude::*;

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
    #[getter]
    fn user(&self) -> i32 {
        self.event.uid
    }

    #[getter]
    fn group(&self) -> i32 {
        self.event.gid
    }

    #[getter]
    fn subject(&self) -> PySubject {
        let path = if let Some(SubjPart::Exe(path)) = self.event.subj.parts.iter().find(|p| match p
        {
            SubjPart::Exe(_) => true,
            _ => false,
        }) {
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

    #[getter]
    fn object(&self) -> PyObject {
        let path = if let Some(ObjPart::Path(path)) =
            self.event.obj.parts.iter().find(|p| match p {
                ObjPart::Path(_) => true,
                _ => false,
            }) {
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

#[pyclass(module = "log", name = "Subject")]
#[derive(Clone)]
pub struct PySubject {
    file: String,
    trust: String,
    access: String,
}

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
    #[getter]
    fn file(&self) -> String {
        self.file.clone()
    }
    #[getter]
    fn trust(&self) -> String {
        self.trust.clone()
    }
    #[getter]
    fn access(&self) -> String {
        self.access.clone()
    }
}

#[pymethods]
impl PyObject {
    #[getter]
    fn file(&self) -> String {
        self.file.clone()
    }
    #[getter]
    fn trust(&self) -> String {
        self.trust.clone()
    }
    #[getter]
    fn access(&self) -> String {
        self.access.clone()
    }
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
