/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::process::Command;

use crate::error::Error;
use nom::character::complete::line_ending;
use nom::combinator::iterator;
use nom::sequence::terminated;

use crate::error::Error::UserGroupLookupFailure;
use crate::users::{parse, Group, User};

pub fn users() -> Result<Vec<User>, Error> {
    read_db("passwd", parse::user)
}

pub fn groups() -> Result<Vec<Group>, Error> {
    read_db("group", parse::group)
}

fn read_db<O, F: Fn(&str) -> nom::IResult<&str, O>>(name: &str, p: F) -> Result<Vec<O>, Error> {
    let res = Command::new("getent")
        .arg(name)
        .output()
        .map_err(|_| UserGroupLookupFailure(name.to_string()))?;

    let s = String::from_utf8(res.stdout)?;
    let r = iterator(&*s, terminated(p, line_ending)).collect();
    Ok(r)
}
