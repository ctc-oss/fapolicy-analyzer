use std::path::Path;

use clap::Clap;
use lmdb::{DatabaseFlags, Environment, Transaction, WriteFlags};

use fapolicy_analyzer::cfg::All;
use fapolicy_analyzer::rpm::load_system_trust;

#[derive(Clap)]
#[clap(name = "trustdb_init")]
/// Initialize a fapolicyd Trust Database
/// Default behavior is to read from the RPM database
/// Empty database creation is possible using the `--emtpy` flag
struct Opts {
    /// create an empty database
    #[clap(long)]
    empty: bool,

    /// Max size, in bytes, of the database backend
    #[clap(long, default_value = "104857600")]
    size: usize,

    /// Directory in which to create the database
    dbdir: String,
}

fn main() {
    let opts: Opts = Opts::parse();
    let path = Path::new(&opts.dbdir);
    if !path.exists() {
        panic!("dbdir does not exist")
    } else if !path.is_dir() {
        panic!("dbdir must be a directory")
    }

    let env = Environment::new()
        .set_max_dbs(1)
        .set_map_size(opts.size)
        .open(path)
        .expect("unable to open path to trust db");

    let db = env
        .create_db(Some("trust.db"), DatabaseFlags::DUP_SORT)
        .expect("failed to create db");

    if !opts.empty {
        let cfg = All::load();
        let sys = load_system_trust(&cfg.system.system_trust_path);

        let mut tx = env.begin_rw_txn().expect("failed to start db transaction");
        for trust in sys {
            let v = format!("{} {} {}", 1, trust.size, trust.hash);
            tx.put(db, &trust.path, &v, WriteFlags::APPEND_DUP)
                .expect("unable to add trust to db transaction");
        }
        tx.commit().expect("failed to commit db transaction")
    }
}
