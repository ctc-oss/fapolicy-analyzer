/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::error::Error;
use crate::error::Error::NativeInitFail;
use crate::event::{Event, Parser};
use crate::record::Type;
use auparse_sys::*;
use std::ffi::c_void;
use std::path::Path;
use std::ptr;
use std::ptr::NonNull;

pub type Filter = fn(Type) -> bool;

pub struct Logs<T, E> {
    au: NonNull<auparse_state_t>,
    p: Box<dyn Parser<T, Error = E>>,
    f: Option<Filter>,
}

impl<T, E> Iterator for Logs<T, E> {
    type Item = T;

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            match Event::from(self.au) {
                Some(next) => {
                    let e = match self.f {
                        Some(filter) => {
                            if filter(next.t0().into()) {
                                next
                            } else {
                                continue;
                            }
                        }
                        None => next,
                    };
                    match self.p.parse(e) {
                        Ok(i) => return Some(i),
                        Err(_) => continue,
                    }
                }
                None => return None,
            }
        }
    }
}

impl<T, E> Drop for Logs<T, E> {
    fn drop(&mut self) {
        unsafe {
            auparse_destroy(self.au.as_ptr());
        }
    }
}

impl<T, E> Logs<T, E> {
    pub fn all(p: Box<dyn Parser<T, Error = E>>) -> Result<Self, Error> {
        Self::new(p, None, None)
    }
    pub fn filtered(p: Box<dyn Parser<T, Error = E>>, filter: Filter) -> Result<Self, Error> {
        Self::new(p, Some(filter), None)
    }
    fn new(
        p: Box<dyn Parser<T, Error = E>>,
        f: Option<Filter>,
        path: Option<&Path>,
    ) -> Result<Self, Error> {
        let au = match path {
            None => unsafe { auparse_init(ausource_t_AUSOURCE_LOGS, ptr::null()) },
            Some(p) => unsafe {
                let file_path = p.display().to_string();
                auparse_init(
                    ausource_t_AUSOURCE_FILE,
                    file_path.as_ptr() as *const c_void,
                )
            },
        };
        match NonNull::new(au) {
            Some(au) => Ok(Self { au, p, f }),
            None => Err(NativeInitFail),
        }
    }

    pub fn all_from(path: &Path, p: Box<dyn Parser<T, Error = E>>) -> Result<Self, Error> {
        Self::new(p, None, Some(path))
    }
    pub fn filtered_from(
        path: &Path,
        p: Box<dyn Parser<T, Error = E>>,
        filter: Filter,
    ) -> Result<Self, Error> {
        Self::new(p, Some(filter), Some(path))
    }
}
