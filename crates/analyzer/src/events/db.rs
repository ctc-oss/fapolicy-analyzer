use crate::events::event::Event;
use std::slice::Iter;

#[derive(Clone)]
pub struct DB {
    pub(crate) events: Vec<Event>,
}

impl Default for DB {
    fn default() -> Self {
        DB { events: vec![] }
    }
}

impl DB {
    pub fn from(es: Vec<Event>) -> Self {
        DB { events: es }
    }

    /// Get an iterator to the underlying events
    pub fn iter(&self) -> Iter<'_, Event> {
        self.events.iter()
    }
}
