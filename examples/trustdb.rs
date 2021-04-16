use clap::Clap;
use lmdb::{DatabaseFlags, Environment};
use std::path::Path;

#[derive(Clap)]
struct Opts {
    #[clap(long)]
    empty: bool,

    path: String,
}

fn main() {
    let opts: Opts = Opts::parse();

    if opts.empty {
        let env = Environment::new()
            .set_max_dbs(1)
            .open(Path::new(&opts.path))
            .expect("unable to open path to trust db");

        env.create_db(Some("trust.db"), DatabaseFlags::DUP_SORT)
            .expect("failed to create db");
    } else {
        println!("non-empty init is not yet supported")
    }
}
