use auparse_sys::event::Event;
use fapolicy_auparse::error::Error;
use fapolicy_auparse::logs::Logs;
use fapolicy_auparse::record;
use fapolicy_auparse::record::Type::Fanotify;
use std::time::SystemTime;

#[derive(Debug)]
struct FanEvent {
    pub time: SystemTime,
    pub t0: record::Type,

    pub uid: i32,
    pub gid: i32,
}

fn parse(e: Event) -> Option<FanEvent> {
    Some(FanEvent {
        time: e.time(),
        t0: e.t0().into(),
        uid: e.int("uid").expect("uid"),
        gid: e.int("gid").expect("gid"),
    })
}

fn main() -> Result<(), Error> {
    Logs::filtered(parse, |x| x == Fanotify)?.for_each(|e| println!("{:?}", e));
    Ok(())
}
