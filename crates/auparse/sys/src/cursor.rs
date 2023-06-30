use crate::error::Error;
use crate::event::Event;
use crate::util::{audit_get_int, audit_get_str};
use crate::{
    auparse_destroy, auparse_get_time, auparse_get_type, auparse_next_event, auparse_state_t,
};
use std::ptr::NonNull;

pub struct Cursor {
    au: NonNull<auparse_state_t>,
}

impl Cursor {
    pub fn new(au: NonNull<auparse_state_t>) -> Self {
        Cursor { au }
    }
}

impl Iterator for Cursor {
    type Item = Event;

    fn next(&mut self) -> Option<Self::Item> {
        unsafe {
            match auparse_next_event(self.au.as_ptr()) {
                1 => Some(Event::new(self.au)),
                _ => None,
            }
        }
    }
}

impl Drop for Cursor {
    fn drop(&mut self) {
        unsafe {
            auparse_destroy(self.au.as_ptr());
        }
    }
}
