use fapolicy_auparse::error::Error;
use fapolicy_auparse::logs::Logs;

fn main() -> Result<(), Error> {
    let log = Logs::all()?;
    log.for_each(|e| println!("{:?}", e));
    Ok(())
}
