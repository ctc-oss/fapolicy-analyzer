/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::path::PathBuf;

use nom::bytes::complete::{is_not, tag};
use nom::sequence::delimited;

use crate::parser::parse::{StrTrace, TraceResult};

pub(crate) fn parse(i: StrTrace) -> TraceResult<PathBuf> {
    // todo;; fail if the path contains a directory component; we should expect filename only in the marker
    delimited(tag("["), is_not("]"), tag("]"))(i).map(|(r, path)| (r, PathBuf::from(path.current)))
}
