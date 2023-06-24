use auparse_sys::event::Event;
use chrono::{DateTime, Local};
use fapolicy_auparse::error::Error;
use fapolicy_auparse::error::Error::GeneralFail;
use fapolicy_auparse::logs::Logs;
use fapolicy_auparse::record::Type::SystemBoot;
use std::time::{Duration, SystemTime};

struct BootEvent {
    time: u64,
}

fn parse(e: Event) -> Option<BootEvent> {
    Some(BootEvent {
        time: e.ts() as u64,
    })
}

/// Example that behaves like the ubiquitous uptime command
fn main() -> Result<(), Error> {
    let log = Logs::filtered(parse, |t| t == SystemBoot)?;

    // filter the log to boots and take the last one
    let then = log.last().expect("[fail] no boot entries");

    // uptime from then till now
    let now = SystemTime::now();
    let uptime = now.duration_since(std::time::UNIX_EPOCH + Duration::from_secs(then.time))?;

    let datetime: DateTime<Local> = now.into();
    let duration = chrono::Duration::from_std(uptime)
        .map_err(|_| GeneralFail("Duration from uptime".to_string()))?;
    let hours = duration - chrono::Duration::days(duration.num_days());
    let min = duration - chrono::Duration::hours(duration.num_hours());

    // format stdout to look like `uptime`
    println!(
        " {} up {} days, {: >2}:{:02},",
        datetime.format("%T"),
        duration.num_days(),
        hours.num_hours(),
        min.num_minutes()
    );

    Ok(())
}
