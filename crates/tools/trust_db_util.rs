use clap::Clap;

use fapolicy_api::trust::Trust;
use fapolicy_app::cfg;
use fapolicy_daemon::rpm::load_system_trust;
use fapolicy_trust::read;
use fapolicy_util::sha::sha256_digest;
use lmdb::{DatabaseFlags, Environment, Transaction, WriteFlags};
use std::fs::File;
use std::io::BufReader;
use std::path::Path;

#[derive(Clap)]
#[clap(name = "Trust DB Utils", version = "v0.3.0")]
struct Opts {
    #[clap(subcommand)]
    pub cmd: Command,

    /// Specify the fapolicyd database directory
    /// Defaults to the value specified in the users XDG configuration
    dbdir: Option<String>,
}

#[derive(Clap)]
enum Command {
    Init(InitOpts),
    AddRec(AddRecOpts),
    DelRec(DelRecOpts),
    Dump(DumpDbOpts),
    Search(SearchDbOpts),
}

#[derive(Clap)]
struct InitOpts {
    /// create an empty database
    #[clap(long)]
    empty: bool,

    /// Max size, in bytes, of the database backend
    #[clap(long, default_value = "104857600")]
    size: usize,
}

#[derive(Clap)]
struct AddRecOpts {
    /// File to add
    path: String,
}

#[derive(Clap)]
struct DelRecOpts {}

#[derive(Clap)]
struct DumpDbOpts {
    #[clap(long)]
    check: bool,
}

#[derive(Clap)]
struct SearchDbOpts {}

fn main() {
    let sys_conf = cfg::All::load();
    let all_opts: Opts = Opts::parse();
    let trust_db_path = match all_opts.dbdir {
        Some(ref p) => Path::new(p),
        None => Path::new(&sys_conf.system.trust_db_path),
    };

    if !trust_db_path.exists() {
        panic!("dbdir does not exist")
    } else if !trust_db_path.is_dir() {
        panic!("dbdir must be a directory")
    }

    let env = Environment::new()
        .set_max_dbs(1)
        .set_map_size(usize::MAX)
        .open(trust_db_path)
        .expect("unable to open path to trust db");

    match all_opts.cmd {
        Command::Init(opts) => init(opts, &sys_conf, &env),
        Command::AddRec(opts) => add(opts, &sys_conf, &env),
        Command::DelRec(_) => {}
        Command::Dump(opts) => dump(opts, &sys_conf),
        Command::Search(_) => {}
    }
}

fn init(opts: InitOpts, cfg: &cfg::All, env: &Environment) {
    let db = env
        .create_db(Some("trust.db"), DatabaseFlags::DUP_SORT)
        .expect("failed to create db");

    if opts.empty {
        return;
    }

    let sys = load_system_trust(&cfg.system.system_trust_path).expect("load sys trust error");

    let mut tx = env.begin_rw_txn().expect("failed to start db transaction");
    for trust in sys {
        let v = format!("{} {} {}", 1, trust.size, trust.hash);
        tx.put(db, &trust.path, &v, WriteFlags::APPEND_DUP)
            .expect("unable to add trust to db transaction");
    }
    tx.commit().expect("failed to commit db transaction")
}

fn add(opts: AddRecOpts, _: &cfg::All, env: &Environment) {
    let trust = new_trust_record(&opts.path).expect("unable to generate trust");
    let db = env.open_db(Some("trust.db")).expect("failed to open db");

    let mut tx = env.begin_rw_txn().expect("failed to start db transaction");
    let v = format!("{} {} {}", 2, trust.size, trust.hash);
    tx.put(db, &trust.path, &v, WriteFlags::APPEND_DUP)
        .expect("unable to add trust to db transaction");
    tx.commit().expect("failed to commit db transaction")
}

fn dump(_: DumpDbOpts, cfg: &cfg::All) {
    let db = read::load_trust_db(&cfg.system.trust_db_path).expect("failed to load db");
    db.iter()
        .for_each(|(k, v)| println!("{} {} {}", k, v.trusted.size, v.trusted.hash))
}

fn new_trust_record(path: &str) -> Result<Trust, String> {
    let f = File::open(path).map_err(|_| "failed to open file".to_string())?;
    let sha = sha256_digest(BufReader::new(&f)).map_err(|_| "failed to hash file".to_string())?;

    Ok(Trust {
        path: path.to_string(),
        size: f.metadata().unwrap().len(),
        hash: sha,
    })
}
