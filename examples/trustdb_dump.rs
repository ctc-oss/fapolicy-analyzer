use std::path::Path;

use clap::Clap;
use lmdb::{Cursor, Environment, Transaction};

#[derive(Clap)]
struct Opts {
    path: String,
}

fn main() {
    let opts: Opts = Opts::parse();
    let path = Path::new(&opts.path);

    let env = Environment::new()
        .set_max_dbs(1)
        .open(path)
        .expect("failed to open trust db environment");

    let db = env
        .open_db(Some("trust.db"))
        .expect("failed to load trust.db");

    env.begin_ro_txn()
        .map(|t| {
            t.open_ro_cursor(db).map(|mut c| {
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
        })
        .unwrap()
        .unwrap()
}
