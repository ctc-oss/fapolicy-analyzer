/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

pub use self::decision::Decision;
pub use self::file_type::Rvalue;
pub use self::object::Object;
pub use self::object::Part as ObjPart;
pub use self::permission::Permission;
pub use self::rule::Rule;
pub use self::set::Set;
pub use self::subject::Part as SubjPart;
pub use self::subject::Subject;

pub mod parser;

mod decision;
mod file_type;
mod object;
pub mod parse;

pub mod db;
pub mod error;
mod permission;
pub mod read;
mod rule;
mod set;
mod subject;

pub(crate) fn bool_to_c(b: bool) -> char {
    if b {
        '1'
    } else {
        '0'
    }
}
