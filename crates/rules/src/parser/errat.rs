/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::parser::error::RuleParseError;
use crate::parser::error::RuleParseError::*;
use crate::parser::parse::StrTrace;
use crate::parser::trace::{Position, Trace};

pub type StrErrorAt<'a> = ErrorAt<StrTrace<'a>>;

#[derive(Debug, PartialEq, Copy, Clone)]
pub struct ErrorAt<I>(pub RuleParseError<I>, pub usize, pub usize);

impl ErrorAt<Trace<&str>> {
    pub fn new<'a>(e: RuleParseError<Trace<&'a str>>, t: Trace<&str>) -> ErrorAt<Trace<&'a str>> {
        ErrorAt(e, t.position(), t.current.len())
    }

    pub fn new_with_len<'a>(
        e: RuleParseError<Trace<&'a str>>,
        t: Trace<&str>,
        len: usize,
    ) -> ErrorAt<Trace<&'a str>> {
        ErrorAt(e, t.position(), len)
    }
}

impl<I> ErrorAt<I> {
    pub fn shift(self, by: usize) -> Self {
        ErrorAt(self.0, self.1 + by, self.2 + by)
    }
}

impl<T, I> From<ErrorAt<I>> for Result<T, nom::Err<ErrorAt<I>>> {
    fn from(e: ErrorAt<I>) -> Self {
        Err(nom::Err::Error(e))
    }
}

impl<'a> From<RuleParseError<StrTrace<'a>>> for ErrorAt<StrTrace<'a>> {
    fn from(e: RuleParseError<StrTrace<'a>>) -> Self {
        let t = match e {
            ExpectedDecision(t) => t,
            UnknownDecision(t, v) => {
                return ErrorAt::<StrTrace<'a>>::new_with_len(e, t, v.current.len())
            }
            ExpectedPermTag(t, v) => {
                return ErrorAt::<StrTrace<'a>>::new_with_len(e, t, v.current.len())
            }
            ExpectedPermType(t, v) => {
                return ErrorAt::<StrTrace<'a>>::new_with_len(e, t, v.current.len())
            }
            ExpectedPermAssignment(t) => return ErrorAt::<StrTrace<'a>>::new_with_len(e, t, 0),
            ExpectedEndOfInput(t) => t,
            ExpectedWhitespace(t) => t,
            MissingSeparator(t) => t,
            MissingSubject(t) => t,
            MissingObject(t) => t,
            MissingBothSubjObj(t) => t,
            UnknownSubjectPart(t) => t,
            SubjectPartExpected(t) => t,
            ExpectedInt(t) => t,

            UnknownObjectPart(t) => t,
            ObjectPartExpected(t) => t,
            ExpectedDirPath(t) => t,
            ExpectedFilePath(t) => t,
            ExpectedPattern(t) => t,
            ExpectedBoolean(t) => t,
            ExpectedFileType(t) => t,

            Nom(t, _) => t,
        };
        ErrorAt::<StrTrace<'a>>::new(e, t)
    }
}

#[cfg(test)]
mod tests {
    use crate::parser::errat::StrErrorAt;
    use crate::parser::error::RuleParseError;
    use crate::parser::parse::StrTrace;

    #[test]
    fn shift_test() {
        let t = StrTrace::new("foo");
        let e = StrErrorAt::new(RuleParseError::ExpectedInt(t), t);
        assert_eq!(t.position, e.1);
        assert_eq!(t.current.len(), e.2);
        assert_eq!(3, e.2);

        let by = 1001;
        let e = e.shift(by);
        assert_eq!(t.position + by, e.1);
        assert_eq!(t.current.len() + by, e.2);
        assert_eq!(3 + by, e.2);
    }
}
