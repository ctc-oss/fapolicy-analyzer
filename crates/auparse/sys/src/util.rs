/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use crate::error::Error;
use crate::error::Error::GetAuditFieldFail;
use crate::{
    auparse_find_field, auparse_find_field_next, auparse_first_record, auparse_get_field_int,
    auparse_get_field_num, auparse_get_field_str, auparse_get_record_num, auparse_goto_field_num,
    auparse_goto_record_num, auparse_next_field, auparse_state_t,
};
use std::ffi::{CStr, CString};
use std::os::raw::c_uint;

pub unsafe fn audit_get_int(au: *mut auparse_state_t, field: &str) -> Result<i32, Error> {
    if let Ok((rec, field)) = find_last_field(au, field) {
        auparse_goto_record_num(au, rec);
        auparse_goto_field_num(au, field);
        let res = auparse_get_field_int(au) as i32;
        auparse_first_record(au);
        Ok(res)
    } else {
        Err(GetAuditFieldFail(field.to_string()))
    }
}

pub unsafe fn audit_get_str(au: *mut auparse_state_t, field: &str) -> Result<String, Error> {
    if let Ok((rec, field)) = find_last_field(au, field) {
        auparse_goto_record_num(au, rec);
        auparse_goto_field_num(au, field);
        let res = auparse_get_field_str(au);
        auparse_first_record(au);

        if !res.is_null() {
            let str = CStr::from_ptr(res);
            let str = str.to_str().unwrap();
            Ok(String::from(str))
        } else {
            Err(GetAuditFieldFail(field.to_string()))
        }
    } else {
        Err(GetAuditFieldFail(field.to_string()))
    }
}

// field names are unique within a record
// an event may contain multple records
// thus an even may contain non-unique field names
// this provides coordinates for the last appearance of a field in an event
// todo;; this is fragile, parsing each record into a structure and querying
//        for fields that can be indentified by sibling fields would be better
unsafe fn find_last_field(
    au: *mut auparse_state_t,
    field: &str,
) -> Result<(c_uint, c_uint), Error> {
    let str = CString::new(field).expect("CString field");
    let tpid = auparse_find_field(au, str.as_ptr());
    let mut coords = None;
    if !tpid.is_null() {
        coords = Some((auparse_get_record_num(au), auparse_get_field_num(au)));
        while !auparse_find_field_next(au).is_null() {
            coords = Some((auparse_get_record_num(au), auparse_get_field_num(au)));
        }
    }

    match coords {
        Some(c) => Ok(c),
        None => Err(GetAuditFieldFail(field.to_string())),
    }
}
