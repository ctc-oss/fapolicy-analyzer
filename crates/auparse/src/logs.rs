/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::audit::Parser;
use crate::record::Type;
use auparse_sys::cursor::Cursor;
use auparse_sys::error::Error;
use auparse_sys::source;
use std::path::Path;

pub type Filter = fn(Type) -> bool;

pub struct Logs<T, E> {
    c: Cursor,
    p: Box<dyn Parser<T, Error = E>>,
    f: Option<Filter>,
}

impl<T, E> Iterator for Logs<T, E> {
    type Item = T;

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            match self.c.next() {
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
                    match self.p.parse(&e) {
                        Ok(i) => return Some(i),
                        Err(e) => {
                            self.p.on_error(e);
                            continue;
                        }
                    }
                }
                None => return None,
            }
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
        let c = match path {
            None => source::logs(),
            Some(p) => source::file(p),
        }?;
        Ok(Self { c, p, f })
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
