use crate::error::Error;
use crate::util::{audit_get_int, audit_get_str};
use crate::{auparse_get_time, auparse_get_type, auparse_next_event, auparse_state_t};
use std::ptr::NonNull;
use std::time::{Duration, SystemTime};

pub type Filter = fn(u32) -> bool;
pub type Parser<T> = fn(Event) -> Option<T>;

pub struct Event {
    au: NonNull<auparse_state_t>,
}

impl Iterator for Event {
    type Item = Event;

    fn next(&mut self) -> Option<Self::Item> {
        unsafe { Event::from(self.au.as_ptr()) }
    }
}

impl Event {
    pub fn t0(&self) -> u32 {
        unsafe { auparse_get_type(self.au.as_ptr()) as u32 }
    }

    pub fn ts(&self) -> i64 {
        unsafe { auparse_get_time(self.au.as_ptr()) as i64 }
    }
    pub fn int(&self, name: &str) -> Result<i32, Error> {
        unsafe { audit_get_int(self.au.as_ptr(), name) }
    }
    pub fn str(&self, name: &str) -> Result<String, Error> {
        unsafe { audit_get_str(self.au.as_ptr(), name) }
    }

    // todo;; pass in Parser<T>, return Option<T>
    pub fn from(ptr: *mut auparse_state_t) -> Option<Event> {
        unsafe {
            match auparse_next_event(ptr) {
                1 => Some(Self {
                    au: NonNull::new(ptr).expect("non null au"),
                }),
                _ => None,
            }
        }
    }
}
