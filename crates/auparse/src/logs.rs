use crate::error::Error;
use crate::error::Error::NativeInitFail;
use crate::record::Type;
use auparse_sys::event::{Event, Parser};
use auparse_sys::*;
use std::ffi::c_void;
use std::path::Path;
use std::ptr;
use std::ptr::NonNull;

pub type Filter = fn(Type) -> bool;

pub struct Logs<T> {
    au: NonNull<auparse_state_t>,
    p: Parser<T>,
    f: Option<Filter>,
}

impl<T> Iterator for Logs<T> {
    type Item = T;

    fn next(&mut self) -> Option<Self::Item> {
        Event::from(self.au.as_ptr())
            .map(|mut e| {
                if let Some(f) = self.f {
                    loop {
                        if let Some(e) = e.next() {
                            if f(e.t0().into()) {
                                return (self.p)(e);
                            } else {
                                continue;
                            }
                        } else {
                            return None;
                        }
                    }
                } else {
                    return (self.p)(e);
                }
            })
            .flatten()
    }
}

impl<T> Drop for Logs<T> {
    fn drop(&mut self) {
        unsafe {
            auparse_destroy(self.au.as_ptr());
        }
    }
}

impl<T> Logs<T> {
    pub fn all(p: Parser<T>) -> Result<Self, Error> {
        Self::new(p, None, None)
    }
    pub fn filtered(p: Parser<T>, filter: Filter) -> Result<Self, Error> {
        Self::new(p, Some(filter), None)
    }
    fn new(p: Parser<T>, f: Option<Filter>, path: Option<&Path>) -> Result<Self, Error> {
        let au = match path {
            None => unsafe { auparse_init(ausource_t_AUSOURCE_LOGS, ptr::null()) },
            Some(p) => unsafe {
                auparse_init(
                    ausource_t_AUSOURCE_FILE,
                    p.display().to_string().as_str().as_ptr() as *mut c_void,
                )
            },
        };
        if au.is_null() {
            Err(NativeInitFail)
        } else {
            Ok(Self {
                au: NonNull::new(au).expect("non null au"),
                p,
                f,
            })
        }
    }

    pub fn all_from(path: &Path, p: Parser<T>) -> Result<Self, Error> {
        Self::new(p, None, Some(path))
    }
    pub fn filtered_from(path: &Path, p: Parser<T>, filter: Filter) -> Result<Self, Error> {
        Self::new(p, Some(filter), Some(path))
    }
}