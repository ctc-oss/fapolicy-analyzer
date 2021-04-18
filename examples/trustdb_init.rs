use std::path::Path;

use clap::Clap;
use lmdb::{DatabaseFlags, Environment, Transaction, WriteFlags};

use fapolicy_analyzer::cfg::All;
use fapolicy_analyzer::rpm::load_system_trust;

#[derive(Clap)]
struct Opts {
    #[clap(long)]
    empty: bool,

    #[clap(long, default_value = "104857600")]
    size: usize,

    path: String,
}

fn main() {
    let opts: Opts = Opts::parse();

    let env = Environment::new()
        .set_max_dbs(1)
        .set_map_size(opts.size)
        .open(Path::new(&opts.path))
        .expect("unable to open path to trust db");

    let db = env
        .create_db(Some("trust.db"), DatabaseFlags::DUP_SORT)
        .expect("failed to create db");

    if !opts.empty {
        let cfg = All::load();
        let sys = load_system_trust(&cfg.system.system_trust_path);

        env.begin_rw_txn()
            .map(|mut tx| {
                for trust in sys {
                    let v = format!("{} {} {}", 1, trust.size, trust.hash);
                    tx.put(db, &trust.path, &v, WriteFlags::APPEND_DUP)
                        .expect("unable to write record");
                }
                tx.commit().expect("unable to commit trust records")
            })
            .unwrap();
    }
}
