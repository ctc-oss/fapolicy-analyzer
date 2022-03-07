extern crate nom;

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

#[derive(Debug, Copy, Clone)]
struct Trace<I> {
    remaining: I,
    // copy of orginal text
    original: I,
    // current position relative to original
    position: usize,
}

impl<T> core::ops::Deref for Trace<T> {
    type Target = T;
    fn deref(&self) -> &Self::Target {
        &self.remaining
    }
}

impl<I> Trace<I>
where
    I: Clone,
{
    pub fn new(v: I) -> Self {
        Trace {
            original: v.clone(),
            remaining: v,
            position: 0,
        }
    }
}

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
type StrTraceError<'a> = CustomError<StrTrace<'a>>;
type StrTraceResult<'a> = IResult<StrTrace<'a>, Product, StrTraceError<'a>>;

#[derive(Debug, PartialEq)]
enum CustomError<I> {
    ExpectedAlpha,
    Nom(I, ErrorKind),
}

impl<I> ParseError<I> for CustomError<I> {
    fn from_error_kind(input: I, kind: ErrorKind) -> Self {
        CustomError::Nom(input, kind)
    }

    fn append(_: I, _: ErrorKind, other: Self) -> Self {
        other
    }
}

fn is_alpha(input: StrTrace) -> StrTraceResult {
    alpha1(input).map(|(t, r)| {
        (
            t,
            Product {
                txt: r.remaining.to_string(),
            },
        )
    })
}

fn is_alpha_twice(i: StrTrace) -> StrTraceResult {
    match nom::combinator::complete(nom::sequence::tuple((alpha1, space1, alpha1)))(i) {
        Ok((trace, (a, _, b))) => Ok((
            trace,
            Product {
                txt: b.remaining.to_string(),
            },
        )),
        Err(e) => Err(e),
    }
}

fn eq_tag(i: StrTrace) -> IResult<StrTrace, StrTrace, StrTraceError> {
    verify(take(1usize), |t: &StrTrace| t.remaining.take(1) == "=")(i)
}

fn is_assignment(i: StrTrace) -> IResult<StrTrace, Assignment, StrTraceError> {
    match nom::combinator::complete(nom::sequence::tuple((alpha1, eq_tag, alphanumeric1)))(i) {
        Ok((trace, (a, _, b))) => Ok((
            trace,
            Assignment {
                lhs: a.remaining.to_string(),
                rhs: b.remaining.to_string(),
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

    Ok(())
}

//////////////////////////////////////

impl<I: InputLength> InputLength for Trace<I> {
    fn input_len(&self) -> usize {
        self.remaining.input_len()
    }
}

impl<'a, I> InputIter for Trace<I>
where
    I: InputIter,
{
    type Item = I::Item;
    type Iter = I::Iter;
    type IterElem = I::IterElem;

    fn iter_indices(&self) -> Self::Iter {
        todo!()
    }

    fn iter_elements(&self) -> Self::IterElem {
        todo!()
    }

    fn position<P>(&self, predicate: P) -> Option<usize>
    where
        P: Fn(Self::Item) -> bool,
    {
        self.remaining.position(predicate)
    }

    fn slice_index(&self, count: usize) -> Result<usize, Needed> {
        self.remaining.slice_index(count)
    }
}

impl<I> InputTake for Trace<I>
where
    Self: Slice<RangeFrom<usize>> + Slice<RangeTo<usize>>,
{
    fn take(&self, count: usize) -> Self {
        self.slice(..count)
    }

    fn take_split(&self, count: usize) -> (Self, Self) {
        (self.slice(count..), self.slice(..count))
    }
}

impl<T: AsBytes> AsBytes for Trace<T> {
    fn as_bytes(&self) -> &[u8] {
        self.remaining.as_bytes()
    }
}

impl<'a, I, R> Slice<R> for Trace<I>
where
    I: Slice<R> + Offset + AsBytes + Slice<RangeTo<usize>> + Clone,
{
    fn slice(&self, range: R) -> Self {
        let remaining = self.remaining.slice(range);
        let position = self.original.as_bytes().len() - remaining.as_bytes().len();
        Trace {
            original: self.original.clone(),
            remaining,
            position,
        }
    }
}

impl<T: AsBytes + Clone> From<T> for Trace<T> {
    fn from(i: T) -> Self {
        Self::new(i)
    }
}

impl<T, U> FindSubstring<U> for Trace<T>
where
    T: FindSubstring<U>,
{
    #[inline]
    fn find_substring(&self, substr: U) -> Option<usize> {
        self.original.find_substring(substr)
    }
}

impl<T> UnspecializedInput for Trace<T> {}
