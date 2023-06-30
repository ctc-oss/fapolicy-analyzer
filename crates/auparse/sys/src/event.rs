use crate::error::Error;
use crate::util::{audit_get_int, audit_get_str};
use crate::{auparse_get_time, auparse_get_type, auparse_state_t};
use std::ptr::NonNull;

pub struct Event {
    au: NonNull<auparse_state_t>,
}

impl Event {
    pub(crate) fn new(au: NonNull<auparse_state_t>) -> Self {
        Self { au }
    }

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
}
