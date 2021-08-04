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
    fn user(&self) -> i32 {
        self.event.uid
    }
    fn group(&self) -> i32 {
        self.event.gid
    }
    fn subject(&self) -> String {
        if let Some(SubjPart::Exe(path)) = self.event.subj.parts.iter().find(|p| match p {
            SubjPart::Exe(_) => true,
            _ => false,
        }) {
            path.clone()
        } else {
            "unknown".into()
        }
    }
    fn object(&self) -> String {
        if let Some(ObjPart::Path(path)) = self.event.obj.parts.iter().find(|p| match p {
            ObjPart::Path(_) => true,
            _ => false,
        }) {
            path.clone()
        } else {
            "unknown".into()
        }
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyEvent>()?;
    Ok(())
}
