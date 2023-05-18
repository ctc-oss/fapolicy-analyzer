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
use std::collections::HashMap;
use std::hash::Hash;

pub mod ops;
pub mod parser;

mod decision;
mod dir_type;
mod file_type;
mod linter;
mod object;

pub mod db;
pub mod error;
pub mod load;

mod permission;
mod rule;
mod set;
mod subject;

pub mod read;
pub mod write;

pub(crate) fn bool_to_c(b: bool) -> char {
    if b {
        '1'
    } else {
        '0'
    }
}

pub(crate) fn hasher<T>(items: &[T]) -> HashMap<&T, usize>
where
    T: Eq + Hash,
{
    let mut map = HashMap::new();
    for i in items {
        *map.entry(i).or_insert(0) += 1
    }
    map
}
