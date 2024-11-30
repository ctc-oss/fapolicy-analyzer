use fapolicy_daemon::stats;
use std::sync::{Arc, Mutex};

#[test]
fn parse_stat_rec() {
    let rec = stats::parse("tests/data/state.0").expect("failed to parse state");
    println!("{:?}", rec);
}
