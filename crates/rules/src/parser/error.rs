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
    SubjectPartExpected(I),
    SubjectPartExpectedInt(I),
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
            UnknownSubjectPart(_) => f.write_str("Expected one of ....."),
            SubjectPartExpected(_) => f.write_str("Expected Subject part"),
            SubjectPartExpectedInt(_) => f.write_str("Expected integer value"),
            e @ Nom(_, _) => f.write_fmt(format_args!("{:?}", e)),
        }
    }
}
