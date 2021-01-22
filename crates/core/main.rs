use clap::Clap;

use fapolicyd_trust;
use fapolicyd_trust::FileTrustDB;

#[derive(Clap)]
#[clap(version = "v0.2.0")]
/// File Access Policy Analyzer
struct Opts {
    /// path to trust database
    #[clap(long, default_value = "/etc/fapolicyd/fapolicyd.trust")]
    db: String,
}

fn main() {
    let opts: Opts = Opts::parse();

    let db = FileTrustDB::new(&opts.db);
    for e in db.entries() {
        println!("{} {} {}", e.path, e.size, e.hash)
    }
}
