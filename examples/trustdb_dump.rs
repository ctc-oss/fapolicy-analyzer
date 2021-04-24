use std::path::Path;

use clap::Clap;
use lmdb::{Cursor, Environment, Transaction};

use fapolicy_analyzer::cfg::All;

#[derive(Clap)]
struct Opts {
    path: Option<String>,
}

fn main() {
    let opts: Opts = Opts::parse();
    let path = match opts.path {
        Some(p) => p.clone(),
        None => All::load().system.trust_db_path,
    };
    let path = Path::new(&path);

    let env = Environment::new()
        .set_max_dbs(1)
        .open(path)
        .expect("failed to open trust db environment");

    let db = env
        .open_db(Some("trust.db"))
        .expect("failed to load trust.db");

    let tx = env.begin_ro_txn().expect("failed to start transaction");

    tx.open_ro_cursor(db)
        .map(|mut c| {
            c.iter()
                .map(|c| c.unwrap())
                .map(|(k, v)| {
                    (
                        String::from_utf8(Vec::from(k)).unwrap(),
                        String::from_utf8(Vec::from(v)).unwrap(),
                    )
                })
                .for_each(|(k, v)| println!("{} {}", k, v))
        })
        .expect("failed to read db")
}
