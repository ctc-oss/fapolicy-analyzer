use crate::parse::StrTrace;
use crate::parser::error::RuleParseError;
use crate::parser::error::RuleParseError::*;
use crate::parser::trace::{Position, Trace};

pub(crate) type StrErrorAt<'a> = ErrorAt<StrTrace<'a>>;

#[derive(Debug, PartialEq, Copy, Clone)]
pub struct ErrorAt<I>(RuleParseError<I>, usize, usize);

impl ErrorAt<Trace<&str>> {
    pub fn new<'a>(e: RuleParseError<Trace<&'a str>>, t: Trace<&str>) -> ErrorAt<Trace<&'a str>> {
        ErrorAt(e.clone(), t.position(), t.fragment.len())
    }

    pub fn new_with_len<'a>(
        e: RuleParseError<Trace<&'a str>>,
        t: Trace<&str>,
        len: usize,
    ) -> ErrorAt<Trace<&'a str>> {
        ErrorAt(e.clone(), t.position(), len)
    }
}

impl<T, I> Into<Result<T, nom::Err<ErrorAt<I>>>> for ErrorAt<I> {
    fn into(self) -> Result<T, nom::Err<ErrorAt<I>>> {
        Err(nom::Err::Error(self))
    }
}

impl<'a> From<RuleParseError<StrTrace<'a>>> for ErrorAt<StrTrace<'a>> {
    fn from(e: RuleParseError<StrTrace<'a>>) -> Self {
        let t = match e {
            ExpectedDecision(t) => t,
            UnknownDecision(t, v) => {
                return ErrorAt::<StrTrace<'a>>::new_with_len(e, t, v.fragment.len())
            }
            ExpectedPermTag(t, v) => {
                return ErrorAt::<StrTrace<'a>>::new_with_len(e, t, v.fragment.len())
            }
            ExpectedPermType(t, v) => {
                return ErrorAt::<StrTrace<'a>>::new_with_len(e, t, v.fragment.len())
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
