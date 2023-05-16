/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::parser::trace::Trace;
use nom::error::{ErrorKind, ParseError};
use std::fmt::{Display, Formatter};
use RuleParseError::*;

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum RuleParseError<I> {
    ExpectedDecision(I),
    UnknownDecision(I, I),
    ExpectedPermTag(I, I),
    ExpectedPermType(I, I),
    ExpectedPermAssignment(I),
    ExpectedEndOfInput(I),
    ExpectedWhitespace(I),
    MissingSeparator(I),
    MissingSubject(I),
    MissingObject(I),
    MissingBothSubjObj(I),

    UnknownSubjectPart(I),
    UnknownObjectPart(I),

    SubjectPartExpected(I),
    ObjectPartExpected(I),

    ExpectedInt(I),

    ExpectedDirPath(I),
    ExpectedFilePath(I),
    ExpectedPattern(I),
    ExpectedBoolean(I, I),
    ExpectedFileType(I),

    Nom(I, ErrorKind),
}

impl<I> ParseError<I> for RuleParseError<I> {
    fn from_error_kind(input: I, kind: ErrorKind) -> Self {
        RuleParseError::Nom(input, kind)
    }

    fn append(_: I, _: ErrorKind, other: Self) -> Self {
        other
    }
}

impl Display for RuleParseError<Trace<&str>> {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            ExpectedDecision(_) => f.write_str("Expected Decision"),
            UnknownDecision(_, _) => f.write_str("Unknown Decision"),
            ExpectedPermTag(_, _) => f.write_str("Expected tag 'perm'"),
            ExpectedPermType(_, _) => f.write_str("Expected one of 'any', 'open', 'execute'"),
            ExpectedPermAssignment(_) => f.write_str("Expected assignment (=)"),
            ExpectedEndOfInput(_) => f.write_str("Unexpected trailing chars"),
            ExpectedWhitespace(_) => f.write_str("Expected whitespace"),
            MissingSeparator(_) => f.write_str("Missing colon separator"),
            MissingSubject(_) => f.write_str("Missing Subject"),
            MissingObject(_) => f.write_str("Expected Object"),
            MissingBothSubjObj(_) => f.write_str("Missing Subject and Object"),
            UnknownSubjectPart(_) => f.write_str("Unrecognized Subject keyword"),
            UnknownObjectPart(_) => f.write_str("Unrecognized Object keyword"),
            SubjectPartExpected(_) => f.write_str("Expected a Subject part"),
            ObjectPartExpected(_) => f.write_str("Expected an Object part"),
            ExpectedInt(_) => f.write_str("Expected integer value"),
            ExpectedDirPath(_) => f.write_str("Expected dir path"),
            ExpectedFilePath(_) => f.write_str("Expected file path"),
            ExpectedPattern(_) => f.write_str("Expected pattern"),
            ExpectedBoolean(_, _) => f.write_str("Expected boolean (0, 1) value"),
            ExpectedFileType(_) => f.write_str("Expected mime file type"),
            e @ Nom(_, _) => f.write_fmt(format_args!("{:?}", e)),
        }
    }
}
