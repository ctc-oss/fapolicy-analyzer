use crate::parser::error::RuleParseError;
use crate::parser::trace::Trace;
use nom::bytes::complete::tag;
use nom::IResult;

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
