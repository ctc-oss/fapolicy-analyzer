use crate::conf::error::Error;
use crate::Config;
use fapolicy_rules::parser::error::RuleParseError::{ExpectedPermAssignment, ExpectedPermTag};
use nom::branch::alt;
use nom::bytes::complete::tag;
use nom::character::complete::alphanumeric1;
use nom::combinator::opt;
use nom::sequence::tuple;
use nom::{IResult, Parser};

type Res<'a, R> = IResult<&'a str, R, Error>;

fn parse_bool(i: &str) -> Res<bool> {
    match tag("0").parse(i) {
        Ok((i, _)) => Ok((i, false)),
    }
}

#[cfg(test)]
mod tests {
    use crate::conf::parse::parse_bool;
    use assert_matches::assert_matches;

    #[test]
    fn test_parse_bool() {
        assert_matches!(parse_bool("0"), Ok((_, false)))
    }
}
