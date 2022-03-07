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
