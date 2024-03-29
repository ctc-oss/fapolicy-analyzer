/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fmt::{Display, Formatter};

use crate::set::Set;

#[derive(Clone, Debug, Eq, PartialEq, Hash)]
pub enum Rvalue {
    Any,
    Literal(String),
    SetRef(Set),
}

impl Rvalue {
    pub fn new_mime_type(name: &str) -> Rvalue {
        Rvalue::Literal(name.into())
    }
}

impl Display for Rvalue {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Rvalue::Any => f.write_str("any"),
            Rvalue::Literal(l) => f.write_fmt(format_args!("{}", l)),
            Rvalue::SetRef(m) => f.write_fmt(format_args!("{}", m.name)),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn display() {
        let ft1 = Rvalue::new_mime_type("text/x-lua");
        assert_eq!(format!("{}", ft1), format!("{}", &ft1));
    }

    #[test]
    fn macro_mime_list() {
        let l = "application/x-bytecode.ocaml,application/x-bytecode.python,application/java-archive,text/x-java";
        let t = Set::new("lang", l.split(',').map(|s| s.into()).collect());
        assert_eq!(format!("%lang={}", l), format!("{}", t));
    }
}
