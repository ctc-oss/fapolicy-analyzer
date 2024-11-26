use fapolicy_daemon::stats;
use std::sync::{Arc, Mutex};

#[test]
fn parse_stat_rec() {
    let rec = stats::parse("tests/data/state.0").expect("failed to parse state");
    println!("{:?}", rec);
}

// #[test]
// fn watch_stat_changes() {
//     let db = Arc::new(Mutex::new(stats::Db::new()));
//     let f = tempfile::NamedTempFile::new().expect("failed to create temp file");
//     let rx =
//         stats::read(&f.path().display().to_string(), db.clone()).expect("failed to read stats");
//
//     println!("=================");
//     for _ in rx.iter() {
//         println!("boom")
//     }
// }
