use crate::cursor::Cursor;
use crate::error::Error;
use crate::error::Error::NativeInitFail;
use crate::{auparse_init, ausource_t_AUSOURCE_FILE, ausource_t_AUSOURCE_LOGS};
use std::ffi::c_void;
use std::path::Path;
use std::ptr;
use std::ptr::NonNull;

pub fn logs() -> Result<Cursor, Error> {
    let au = unsafe { auparse_init(ausource_t_AUSOURCE_LOGS, ptr::null()) };
    match NonNull::new(au) {
        Some(au) => Ok(Cursor::new(au)),
        None => Err(NativeInitFail),
    }
}

pub fn file(path: &Path) -> Result<Cursor, Error> {
    let au = unsafe {
        let file_path = path.display().to_string();
        auparse_init(
            ausource_t_AUSOURCE_FILE,
            file_path.as_ptr() as *const c_void,
        )
    };
    match NonNull::new(au) {
        Some(au) => Ok(Cursor::new(au)),
        None => Err(NativeInitFail),
    }
}
