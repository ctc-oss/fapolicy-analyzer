use fapolicy_daemon::stats;
use std::sync::atomic::AtomicBool;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

fn main() {
    let kill_flag = Arc::new(AtomicBool::new(false));

    let db = Arc::new(Mutex::new(stats::Db::default()));
    let f = tempfile::NamedTempFile::new().expect("failed to create temp file");
    let rx = stats::read("/var/run/fapolicyd/fapolicyd.state", kill_flag.clone())
        .expect("failed to read stats");

    for rec in rx.iter() {
        let mut db = db.lock().expect("failed to lock");
        db.pruned_insert(Instant::now(), Duration::from_secs(30), rec);
        let avg = db.avg(Duration::from_secs(10));
        println!("{avg:?}")
    }
}
