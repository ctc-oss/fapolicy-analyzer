/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fmt::{Display, Formatter};

/// # Set
/// Set is a named group of values of the same type.
///
/// - Fapolicyd internally distinguishes between INT and STRING set types.
/// - You can define your own set and use it as a value for a specific rule attribute.
/// - The definition is in `key=value` syntax and starts with a set name.
/// - The set name has to start with `%` and the rest is alphanumeric or `_`. The value is a comma separated list.
/// - The set type is inherited from the first item in the list.
/// - If that can be turned into number then whole list is expected to carry numbers.
/// - One can use these sets as a value for subject and object attributes.
/// - It is also possible to use a plain list as an attribute value without previous definition.
/// - The assigned set has to match the attribute type. It is not possible set groups for `TRUST` and `PATTERN` attributes.
///
#[derive(Clone, Debug, PartialEq)]
pub struct Set {
    pub name: String,
    pub values: Vec<String>,
}

impl Set {
    pub fn new(name: &str, list: Vec<String>) -> Self {
        Set {
            name: name.into(),
            values: list,
        }
    }
}

impl Display for Set {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let list: String = self.values.join(",");
        f.write_fmt(format_args!("%{}={}", &self.name, list))
    }
}
