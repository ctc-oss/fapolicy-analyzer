use crate::error::Error;
use crate::error::Error::GetAuditFieldFail;
use crate::{
    auparse_find_field, auparse_first_record, auparse_get_field_int, auparse_get_field_str,
    auparse_state_t,
};
use std::ffi::{CStr, CString};

pub unsafe fn audit_get_int(au: *mut auparse_state_t, field: &str) -> Result<i32, Error> {
    let str = CString::new(field).expect("CString");
    let tpid = auparse_find_field(au, str.as_ptr());
    if !tpid.is_null() {
        let res = auparse_get_field_int(au) as i32;
        auparse_first_record(au);
        Ok(res)
    } else {
        Err(GetAuditFieldFail(field.to_string()))
    }
}

pub unsafe fn audit_get_str(au: *mut auparse_state_t, field: &str) -> Result<String, Error> {
    let str = CString::new(field).expect("CString");
    let tpid = auparse_find_field(au, str.as_ptr());
    if !tpid.is_null() {
        let res = auparse_get_field_str(au);
        auparse_first_record(au);

        if !res.is_null() {
            let str = CStr::from_ptr(res);
            let str = str.to_str().unwrap();
            Ok(String::from(str.to_owned()))
        } else {
            Err(GetAuditFieldFail(field.to_string()))
        }
    } else {
        Err(GetAuditFieldFail(field.to_string()))
    }
}
