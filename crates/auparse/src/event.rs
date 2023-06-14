use crate::filter::Filter;
use crate::record::Type;
use auparse_sys::*;
use std::time::{Duration, SystemTime};

#[derive(Debug)]
pub struct Event {
    pub time: SystemTime,
}

impl Event {
    pub(crate) unsafe fn next(ptr: *mut auparse_state_t, f: Option<Filter>) -> Option<Event> {
        if let Some(f) = f {
            loop {
                match auparse_next_event(ptr) {
                    1 => {
                        let t = auparse_get_type(ptr) as u32;
                        if f(t.into()) {
                            return Some(Event::parse(ptr));
                        } else {
                            continue;
                        }
                    }
                    _ => return None,
                }
            }
        } else {
            match auparse_next_event(ptr) {
                1 => return Some(Event::parse(ptr)),
                _ => return None,
            }
        }
    }

    pub(crate) unsafe fn parse(ptr: *mut auparse_state_t) -> Event {
        let tid = auparse_get_type(ptr) as u32;
        let ts = auparse_get_time(ptr) as u64;
        let time = std::time::UNIX_EPOCH + Duration::from_secs(ts as u64);

        Event { time }
    }
}
