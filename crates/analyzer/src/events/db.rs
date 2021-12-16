use crate::events::event::Event;
use std::slice::Iter;

#[derive(Default, Clone)]
pub struct DB {
    pub(crate) events: Vec<Event>,
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
