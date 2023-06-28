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
