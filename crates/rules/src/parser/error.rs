use nom::error::{ErrorKind, ParseError};
use std::fmt::{Display, Formatter};
use RuleParseError::*;

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum RuleParseError<I> {
    ExpectedDecision,
    UnknownDecision,
    ExpectedPermTag,
    ExpectedPermType,
    ExpectedPermAssignment,
    ExpectedEndOfInput,
    ExpectedWhitespace,
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

impl Display for RuleParseError<&str> {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            ExpectedDecision => f.write_str("Expected Decision"),
            UnknownDecision => f.write_str("Unknown Decision"),
            ExpectedPermTag => f.write_str("Expected tag 'perm'"),
            ExpectedPermType => f.write_str("Expected one of 'any', 'open', 'execute'"),
            ExpectedPermAssignment => f.write_str("Expected assignment (=)"),
            ExpectedEndOfInput => f.write_str("Unexpected trailing chars"),
            ExpectedWhitespace => f.write_str("Expected whitespace"),
            other => f.write_fmt(format_args!("{:?}", other)),
        }
    }
}
