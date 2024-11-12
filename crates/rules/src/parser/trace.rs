/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use nom::error::{ErrorKind, ParseError};
use nom::{
    AsBytes, Compare, CompareResult, FindSubstring, IResult, InputIter, InputLength, InputTake,
    InputTakeAtPosition, Needed, Offset, Slice,
};
use std::ops::{RangeFrom, RangeTo};

pub trait Position {
    fn position(&self) -> usize;
}

/// Trace is a nom custom input type that provides context to the parse
/// The trace carries along a copy of the original rule input text
#[derive(Debug, Copy, Clone)]
pub struct Trace<I> {
    // current context input data
    pub current: I,
    // original input data
    original: I,
    // current position, relative to original
    pub position: usize,
}

impl<I> Trace<I>
where
    I: AsBytes + Clone,
{
    pub fn new(i: I) -> Self {
        Trace {
            current: i.clone(),
            original: i,
            position: 0,
        }
    }

    pub fn is_empty(&self) -> bool {
        self.as_bytes().is_empty()
    }
}

impl<I: PartialEq> PartialEq for Trace<I> {
    fn eq(&self, other: &Self) -> bool {
        self.current == other.current
    }
}

impl<I> Position for Trace<I> {
    fn position(&self) -> usize {
        self.position
    }
}

impl<I: Offset> Offset for Trace<I> {
    fn offset(&self, second: &Self) -> usize {
        self.current.offset(&second.current)
    }
}

impl<I: InputLength> InputLength for Trace<I> {
    fn input_len(&self) -> usize {
        self.current.input_len()
    }
}

impl<I> InputIter for Trace<I>
where
    I: InputIter,
{
    type Item = I::Item;
    type Iter = I::Iter;
    type IterElem = I::IterElem;

    fn iter_indices(&self) -> Self::Iter {
        self.current.iter_indices()
    }

    fn iter_elements(&self) -> Self::IterElem {
        self.current.iter_elements()
    }

    fn position<P>(&self, predicate: P) -> Option<usize>
    where
        P: Fn(Self::Item) -> bool,
    {
        self.current.position(predicate)
    }

    fn slice_index(&self, count: usize) -> Result<usize, Needed> {
        self.current.slice_index(count)
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
        self.current.as_bytes()
    }
}

impl<I, R> Slice<R> for Trace<I>
where
    I: Slice<R> + Offset + AsBytes + Slice<RangeTo<usize>> + Clone,
{
    fn slice(&self, range: R) -> Self {
        let current = self.current.slice(range);
        let position = self.original.as_bytes().len() - current.as_bytes().len();
        Trace {
            original: self.original.clone(),
            current,
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
        self.current.find_substring(substr)
    }
}

impl<T: InputLength + InputIter + InputTake + Clone> InputTakeAtPosition for Trace<T>
where
    T: InputTakeAtPosition + InputLength + InputIter,
    Self: Slice<RangeFrom<usize>> + Slice<RangeTo<usize>> + Clone,
{
    type Item = <T as InputIter>::Item;

    fn split_at_position<P, E: ParseError<Self>>(&self, predicate: P) -> IResult<Self, Self, E>
    where
        P: Fn(Self::Item) -> bool,
    {
        match self.current.position(predicate) {
            Some(n) => Ok(self.take_split(n)),
            None => Err(nom::Err::Incomplete(nom::Needed::new(1))),
        }
    }

    fn split_at_position1<P, E: ParseError<Self>>(
        &self,
        _predicate: P,
        _e: ErrorKind,
    ) -> IResult<Self, Self, E>
    where
        P: Fn(Self::Item) -> bool,
    {
        todo!()
    }

    fn split_at_position_complete<P, E: ParseError<Self>>(
        &self,
        predicate: P,
    ) -> IResult<Self, Self, E>
    where
        P: Fn(Self::Item) -> bool,
    {
        match self.split_at_position(predicate) {
            Err(nom::Err::Incomplete(_)) => Ok(self.take_split(self.input_len())),
            res => res,
        }
    }

    fn split_at_position1_complete<P, E: ParseError<Self>>(
        &self,
        predicate: P,
        e: ErrorKind,
    ) -> IResult<Self, Self, E>
    where
        P: Fn(Self::Item) -> bool,
    {
        match self.current.position(predicate) {
            Some(0) => Err(nom::Err::Error(E::from_error_kind(self.clone(), e))),
            Some(n) => Ok(self.take_split(n)),
            None => {
                if self.current.input_len() == 0 {
                    Err(nom::Err::Error(E::from_error_kind(self.clone(), e)))
                } else {
                    Ok(self.take_split(self.input_len()))
                }
            }
        }
    }
}

impl<T: Compare<B>, B: Into<Trace<B>>> Compare<B> for Trace<T> {
    fn compare(&self, t: B) -> CompareResult {
        self.current.compare(t.into().current)
    }

    fn compare_no_case(&self, t: B) -> CompareResult {
        self.current.compare_no_case(t.into().current)
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn trace_tag() {
        //let r = tag("=")(Trace::new("=")).is_ok();
    }
}
