use auparse_sys::event::Event;
use fapolicy_auparse::error::Error;
use fapolicy_auparse::logs::Logs;
use fapolicy_auparse::record;
use std::time::SystemTime;

#[derive(Debug)]
struct AnyEvent {
    pub time: SystemTime,
    pub t0: record::Type,
}

fn parse(e: Event) -> Option<AnyEvent> {
    Some(AnyEvent {
        time: e.time(),
        t0: e.t0().into(),
    })
}

fn main() -> Result<(), Error> {
    let log = Logs::all(parse)?;
    log.for_each(|e| println!("{:?}", e));
    Ok(())
}
