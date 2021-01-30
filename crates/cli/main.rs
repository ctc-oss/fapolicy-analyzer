use clap::Clap;

use fapolicyd::trust::FileTrustDB;

#[derive(Clap)]
#[clap(version = "v0.2.0")]
/// File Access Policy Analyzer
struct Opts {
    /// path to trust database
    #[clap(long, default_value = "/etc/fapolicyd/fapolicyd.trust")]
    db: String,

    #[clap(long)]
    cmd: String,
}

fn main() {
    let opts: Opts = Opts::parse();

    match opts.cmd.as_str() {
        "trust" => {
            let db = FileTrustDB::new(&opts.db);
            for e in db.entries() {
                println!("{} {} {}", e.path, e.size, e.hash)
            }
        }
        "rpm" => {}
        _ => panic!("invalid command"),
    }
}
