use crate::error::Error;
use crate::error::Error::NativeInitFail;
use crate::event::Event;
use crate::filter::Filter;
use auparse_sys::*;
use std::ptr;
use std::ptr::NonNull;

pub struct Logs {
    au: NonNull<auparse_state_t>,
    f: Option<Filter>,
}

impl Iterator for Logs {
    type Item = Event;

    fn next(&mut self) -> Option<Self::Item> {
        unsafe { Event::next(self.au.as_ptr(), self.f) }
    }
}

impl Drop for Logs {
    fn drop(&mut self) {
        unsafe {
            auparse_destroy(self.au.as_ptr());
        }
    }
}

impl Logs {
    pub fn all() -> Result<Self, Error> {
        Self::new(None)
    }
    pub fn filtered(filter: Filter) -> Result<Self, Error> {
        Self::new(Some(filter))
    }
    fn new(filter: Option<Filter>) -> Result<Self, Error> {
        let au = unsafe { auparse_init(ausource_t_AUSOURCE_LOGS, ptr::null()) };
        if au.is_null() {
            Err(NativeInitFail)
        } else {
            Ok(Self {
                au: NonNull::new(au).expect("non null au"),
                f: filter,
            })
        }
    }
}
