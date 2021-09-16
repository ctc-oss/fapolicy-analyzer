use std::path::Path;

use clap::Clap;
use lmdb::{Environment, Transaction, WriteFlags};

use fapolicy_analyzer::api::{Trust, TrustSource};
use fapolicy_analyzer::cfg::All;
use fapolicy_analyzer::sha::sha256_digest;
use std::fs::File;
use std::io::BufReader;

#[derive(Clap)]
#[clap(name = "trustdb_add")]
/// Adds a file directly to the fapolicyd Trust Database
struct Opts {
    /// File to add
    path: String,
}

fn main() {
    let opts: Opts = Opts::parse();
    let path = Path::new(&opts.path);
    if !path.exists() {
        panic!("path does not exist")
    } else if !path.is_file() {
        panic!("path must be a file")
    }
    let trust = new_trust_record(&opts.path).expect("unable to generate trust");

    let cfg = All::load();
    let env = Environment::new()
        .set_max_dbs(1)
        .open(Path::new(&cfg.system.trust_db_path))
        .expect("unable to open path to trust db");

    let db = env.open_db(Some("trust.db")).expect("failed to open db");

    let mut tx = env.begin_rw_txn().expect("failed to start db transaction");
    let v = format!("{} {} {}", 2, trust.size, trust.hash);
    tx.put(db, &trust.path, &v, WriteFlags::APPEND_DUP)
        .expect("unable to add trust to db transaction");
    tx.commit().expect("failed to commit db transaction")
}

fn new_trust_record(path: &str) -> Result<Trust, String> {
    let f = File::open(path).map_err(|_| "failed to open file".to_string())?;
    let sha = sha256_digest(BufReader::new(&f)).map_err(|_| "failed to hash file".to_string())?;

    Ok(Trust {
        path: path.to_string(),
        size: f.metadata().unwrap().len(),
        hash: sha,
        source: TrustSource::Ancillary,
    })
}
