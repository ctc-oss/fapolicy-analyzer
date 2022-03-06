extern crate nom;

use nom::bits::streaming::tag;
use nom::character::complete::alpha1;
use nom::error::ErrorKind;
use nom::error::ParseError;
use nom::Err::Error;
use nom::{
    AsBytes, IResult, InputIter, InputLength, InputTake, Needed, Offset, Slice, UnspecializedInput,
};
use std::ops::{RangeFrom, RangeTo};

#[derive(Debug, Copy, Clone)]
struct Trace<I> {
    src: I,
    txt: I,
}

impl<I> Trace<I>
where
    I: Clone,
{
    pub fn new(v: I) -> Self {
        Trace {
            src: v.clone(),
            txt: v,
        }
    }
}

#[derive(Debug, Clone)]
struct Product {
    txt: String,
}

type StrTrace<'a> = Trace<&'a str>;
type StrTraceError<'a> = CustomError<StrTrace<'a>>;
type StrTraceResult<'a> = IResult<StrTrace<'a>, Product, StrTraceError<'a>>;

#[derive(Debug, PartialEq)]
pub enum CustomError<I> {
    MyError,
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
                txt: r.txt.to_string(),
            },
        )
    })
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let res = is_alpha(Trace::new("foo"))?;
    println!("{:?}", res);

    let res = is_alpha(Trace::new("123")).err();
    println!("{:?}", res);

    Ok(())
}

//////////////////////////////////////

impl<I: InputLength> InputLength for Trace<I> {
    fn input_len(&self) -> usize {
        self.txt.input_len()
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
        self.txt.position(predicate)
    }

    fn slice_index(&self, count: usize) -> Result<usize, Needed> {
        todo!()
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
        self.txt.as_bytes()
    }
}

impl<I> UnspecializedInput for Trace<I> {}

impl<'a, I, R> Slice<R> for Trace<I>
where
    I: Slice<R> + Offset + AsBytes + Slice<RangeTo<usize>> + Clone,
{
    fn slice(&self, range: R) -> Self {
        let next = self.txt.slice(range);
        Trace {
            src: self.src.clone(),
            txt: next,
        }
    }
}
