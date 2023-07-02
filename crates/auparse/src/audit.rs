/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

// export
pub use auparse_sys::cursor::*;
pub use auparse_sys::error::Error;
pub use auparse_sys::event::*;
pub use auparse_sys::source::*;

pub type Filter = fn(u32) -> bool;
pub trait Parser<T> {
    type Error;

    fn parse(&self, e: &Event) -> Result<T, Self::Error>;
    fn on_error(&mut self, _e: Self::Error) {}
}
