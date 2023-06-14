use fapolicy_auparse::error::Error;
use fapolicy_auparse::logs::Logs;
use fapolicy_auparse::record::Type::Fanotify;

fn main() -> Result<(), Error> {
    Logs::filtered(|x| x == Fanotify)?.for_each(|e| println!("{:?}", e));
    Ok(())
}
