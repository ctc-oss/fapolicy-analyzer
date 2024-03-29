/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use nom::branch::alt;
use nom::bytes::complete::tag;

use nom::character::complete::{alpha1, multispace0};

use nom::sequence::{delimited, terminated};

use crate::object::Part as ObjPart;

use crate::parser::error::RuleParseError::*;

use crate::Object;

use crate::parser::parse::{
    dir_type, filepath, filetype, trust_flag, StrTrace, TraceError, TraceResult,
};

fn obj_part(i: StrTrace) -> TraceResult<ObjPart> {
    let (ii, x) = alt((tag("all"), terminated(alpha1, tag("="))))(i)
        .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ObjectPartExpected(i)))?;

    match x.current {
        "all" => Ok((ii, ObjPart::All)),

        "device" => filepath(ii)
            .map(|(ii, d)| (ii, ObjPart::Device(d.current.to_string())))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedFilePath(i))),

        "dir" => dir_type(ii)
            .map(|(ii, d)| (ii, ObjPart::Dir(d)))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedDirPath(i))),

        "ftype" => filetype(ii)
            .map(|(ii, d)| (ii, ObjPart::FileType(d)))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedFileType(i))),

        "path" => filepath(ii)
            .map(|(ii, d)| (ii, ObjPart::Path(d.current.to_string())))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedFilePath(i))),

        "trust" => trust_flag(ii)
            .map(|(ii, d)| (ii, ObjPart::Trust(d)))
            .map_err(|_: nom::Err<TraceError>| nom::Err::Error(ExpectedBoolean(i, ii))),

        _ => Err(nom::Err::Error(UnknownObjectPart(i))),
    }
}

pub(crate) fn parse(i: StrTrace) -> TraceResult<Object> {
    let mut ii = i;
    let mut parts = vec![];
    loop {
        if ii.current.trim().is_empty() {
            break;
        }

        let (i, part) = delimited(multispace0, obj_part, multispace0)(ii)?;
        ii = i;
        parts.push(part);
    }

    // todo;; check for 'all' here, if there are additional entries other than 'trust', its an error

    Ok((ii, Object::new(parts)))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::dir_type::DirType;
    use assert_matches::assert_matches;

    #[test]
    fn parse_obj_part() {
        assert_eq!(ObjPart::All, obj_part("all".into()).ok().unwrap().1);
    }

    #[test]
    fn parse_obj() {
        assert_eq!(
            Object::new(vec![ObjPart::All, ObjPart::Trust(true)]),
            parse("all trust=1".into()).ok().unwrap().1
        );

        assert_eq!(
            Object::new(vec![ObjPart::Trust(true)]),
            parse("trust=1".into()).ok().unwrap().1
        );

        // ordering matters
        assert_eq!(
            Object::new(vec![ObjPart::Trust(true), ObjPart::All]),
            parse("trust=1 all".into()).ok().unwrap().1
        );
    }

    #[test]
    fn unknown_part() {
        assert_matches!(
            obj_part("dir=/tmp".into()).ok().map(|f| f.1),
            Some(ObjPart::Dir(_))
        );
        assert_matches!(
            obj_part("foo=/tmp".into()).err(),
            Some(nom::Err::Error(UnknownObjectPart(_)))
        );
    }

    #[test]
    fn dir_types() {
        assert_matches!(
            obj_part("dir=/tmp".into()).ok().map(|f| f.1),
            Some(ObjPart::Dir(DirType::Path(_)))
        );
        assert_matches!(
            obj_part("dir=tmp".into()).err(),
            Some(nom::Err::Error(ExpectedDirPath(_)))
        );
    }
}
