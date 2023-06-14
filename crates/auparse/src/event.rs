use crate::record::Type;
use auparse_sys::*;
use std::time::{Duration, SystemTime};

#[derive(Debug)]
pub struct Event {
    pub etype: Type,
    pub time: SystemTime,
}

impl Event {
    pub(crate) unsafe fn next(ptr: *mut auparse_state_t) -> Option<Event> {
        match auparse_next_event(ptr) {
            1 => Some(Event::parse(ptr)),
            _ => None,
        }
    }
    pub(crate) unsafe fn parse(ptr: *mut auparse_state_t) -> Event {
        let tid = auparse_get_type(ptr) as u32;
        let ts = auparse_get_time(ptr) as u64;
        let time = std::time::UNIX_EPOCH + Duration::from_secs(ts as u64);
        Event {
            etype: tid.into(),
            time,
        }
    }
}
