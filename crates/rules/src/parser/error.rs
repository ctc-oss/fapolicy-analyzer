use nom::error::{ErrorKind, ParseError};

#[derive(Debug, PartialEq)]
pub enum RuleParseError<I> {
    Generic,
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
