// use crate::error::Error;
// use crate::filter::Filter;
// use crate::record;
// use crate::util::audit_get_int;
// use auparse_sys::*;
// use std::time::{Duration, SystemTime};
//
// #[derive(Debug)]
// pub struct Event {
//     pub time: SystemTime,
//     pub t0: record::Type,
//
//     // todo;; here for demonstration only
//     pub uid: i32,
//     pub gid: i32,
// }
//
// impl Event {
//     // todo;; pass in filter and arser<T>, return Option<T>
//     pub(crate) unsafe fn next(ptr: *mut auparse_state_t, f: Option<Filter>) -> Option<Event> {
//         if let Some(f) = f {
//             loop {
//                 match auparse_next_event(ptr) {
//                     1 => {
//                         let t = auparse_get_type(ptr) as u32;
//                         if f(t.into()) {
//                             match Event::parse(ptr) {
//                                 Ok(e) => return Some(e),
//                                 Err(_) => continue,
//                             }
//                         } else {
//                             continue;
//                         }
//                     }
//                     _ => return None,
//                 }
//             }
//         } else {
//             match auparse_next_event(ptr) {
//                 1 => {
//                     return match Event::parse(ptr) {
//                         Ok(e) => Some(e),
//                         Err(_) => None,
//                     }
//                 }
//                 _ => return None,
//             }
//         }
//     }
//
//     // todo;; this is example of the pluggable logic
//     pub(crate) unsafe fn parse(ptr: *mut auparse_state_t) -> Result<Event, Error> {
//         let tid = auparse_get_type(ptr) as u32;
//         let ts = auparse_get_time(ptr) as u64;
//         let time = std::time::UNIX_EPOCH + Duration::from_secs(ts as u64);
//
//         Ok(Event {
//             time,
//             t0: tid.into(),
//             uid: audit_get_int(ptr, "uid")?,
//             gid: audit_get_int(ptr, "gid")?,
//         })
//     }
// }
