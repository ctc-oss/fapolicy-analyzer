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
            other => f.write_fmt(format_args!("{:?}", other)),
        }
    }
}
