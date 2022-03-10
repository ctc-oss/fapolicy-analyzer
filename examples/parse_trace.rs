extern crate nom;

use fapolicy_rules::parser::error::RuleParseError;
use fapolicy_rules::parser::trace::Trace;
use nom::bytes::complete::tag;
use nom::bytes::complete::take;
use nom::character::complete::{alpha1, alphanumeric1, space1};
use nom::combinator::verify;
use nom::error::ErrorKind;
use nom::error::ParseError;
use nom::{
    AsBytes, AsChar, Compare, CompareResult, ExtendInto, FindSubstring, IResult, InputIter,
    InputLength, InputTake, InputTakeAtPosition, Needed, Offset, Slice, UnspecializedInput,
};
use std::ops::{RangeFrom, RangeTo};

#[derive(Debug, Clone)]
struct Product {
    txt: String,
}

#[derive(Debug, Clone)]
struct Assignment {
    lhs: String,
    rhs: String,
}

type StrTrace<'a> = Trace<&'a str>;
type StrTraceError<'a> = RuleParseError<StrTrace<'a>>;
type StrTraceResult<'a> = IResult<StrTrace<'a>, Product, StrTraceError<'a>>;

fn is_alpha(input: StrTrace) -> StrTraceResult {
    alpha1(input).map(|(t, r)| {
        (
            t,
            Product {
                txt: r.fragment.to_string(),
            },
        )
    })
}

fn is_alpha_twice(i: StrTrace) -> StrTraceResult {
    match nom::combinator::complete(nom::sequence::tuple((alpha1, space1, alpha1)))(i) {
        Ok((trace, (a, _, b))) => Ok((
            trace,
            Product {
                txt: b.fragment.to_string(),
            },
        )),
        Err(e) => Err(e),
    }
}

fn is_assignment(i: StrTrace) -> IResult<StrTrace, Assignment, StrTraceError> {
    match nom::combinator::complete(nom::sequence::tuple((alpha1, tag("="), alphanumeric1)))(i) {
        Ok((trace, (a, _, b))) => Ok((
            trace,
            Assignment {
                lhs: a.fragment.to_string(),
                rhs: b.fragment.to_string(),
            },
        )),
        Err(e) => Err(e),
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // let res = is_alpha(Trace::new("foo"))?;
    // println!("1 {:?}", res);
    //
    // let res = is_alpha(Trace::new("123")).err();
    // println!("2 {:?}", res);
    //
    // let res = is_alpha_twice(Trace::new("foo bar"))?;
    // println!("3 {:?}", res);
    //
    // let res = is_alpha_twice(Trace::new("foo 123")).err();
    // println!("4 {:?}", res);

    let res = is_assignment(Trace::new("foo=123"));
    println!("5 {:?}", res);

    let res = is_assignment(Trace::new("foo123"));
    println!("5 {:?}", res);

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use nom::bytes::complete::tag;
    use nom::IResult;

    #[test]
    fn trace_tag() {
        let r: StrTraceResult = tag("=")(Trace::new("=")).map(|(r, t)| {
            (
                r,
                Product {
                    txt: t.fragment.to_string(),
                },
            )
        });
        assert!(r.is_ok());
        let (x, y) = r.ok().unwrap();
        println!("{:?} {:?}", x, y);
    }
}
