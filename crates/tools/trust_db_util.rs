use clap::Clap;

use crate::Error::{DirTrustError, DpkgCommandFail, DpkgNotFound};
use crate::Subcommand::{Add, Check, Clear, Del, Dump, Init, Search};
use fapolicy_api::trust::Trust;
use fapolicy_app::cfg;
use fapolicy_daemon::rpm::load_system_trust as load_rpm_trust;
use fapolicy_trust::read;
use fapolicy_trust::read::check_trust_db;
use fapolicy_util::sha::sha256_digest;
use lmdb::{DatabaseFlags, Environment, Transaction, WriteFlags};
use rayon::prelude::*;
use std::fs::File;
use std::io;
use std::io::{BufReader, Write};
use std::path::Path;
use std::process::{Command, Output};
use std::time::SystemTime;
use thiserror::Error;

/// An Error that can occur in this app
#[derive(Error, Debug)]
pub enum Error {
    #[error("dpkg-query not found on path")]
    DpkgNotFound,

    #[error("dpkg-query command failed, {0}")]
    DpkgCommandFail(io::Error),

    #[error("cant trust a directory")]
    DirTrustError,

    #[error("file io error, {0}")]
    FileError(#[from] io::Error),

    #[error("file hashing error, {0}")]
    HashError(#[from] fapolicy_util::error::Error),

    #[error("error reading stdout")]
    ParseError(#[from] std::string::FromUtf8Error),
}

#[derive(Clap)]
#[clap(name = "Trust DB Utils", version = "v0.3.0")]
struct Opts {
    #[clap(subcommand)]
    pub cmd: Subcommand,

    /// Specify the fapolicyd database directory
    /// Defaults to the value specified in the users XDG configuration
    dbdir: Option<String>,
}

#[derive(Clap)]
enum Subcommand {
    /// Clear the trust database of all entries
    Clear(ClearOpts),
    /// Initialize the trust database from system trust
    Init(InitOpts),
    /// Add a file to the trust database
    Add(AddRecOpts),
    /// Remove a file from the trust database
    Del(DelRecOpts),
    /// Dump all trust entries to stdout
    Dump(DumpDbOpts),
    /// Search for a trust entry
    Search(SearchDbOpts),
    /// Check trust status
    Check(CheckDbOpts),
}

#[derive(Clap)]
struct ClearOpts {}

#[derive(Clap)]
struct InitOpts {
    /// create an empty database
    #[clap(long)]
    empty: bool,

    /// overwrite existing database
    #[clap(long)]
    force: bool,

    /// use dpkg to generate db
    #[clap(long)]
    dpkg: bool,

    /// number of records to generate
    #[clap(short, long)]
    count: Option<usize>,

    /// use par_iter
    #[clap(long)]
    par: bool,
}

#[derive(Clap)]
struct AddRecOpts {
    /// File to add
    path: String,
}

#[derive(Clap)]
struct DelRecOpts {
    /// File to delete
    path: String,
}

#[derive(Clap)]
struct DumpDbOpts {
    /// Optional file
    #[clap(short, long)]
    outfile: Option<String>,
}

#[derive(Clap)]
struct SearchDbOpts {
    /// File to delete
    #[clap(long)]
    key: String,
}

#[derive(Clap)]
struct CheckDbOpts {
    /// use par_iter
    #[clap(long)]
    par: bool,
}

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

    println!("opening trust db at {}", trust_db_path.to_string_lossy());
    let env = Environment::new()
        .set_max_dbs(1)
        .set_map_size(104857600)
        .open(trust_db_path)
        .expect("unable to open path to trust db");

    match all_opts.cmd {
        Clear(opts) => clear(opts, &sys_conf, &env),
        Init(opts) => init(opts, &sys_conf, &env),
        Add(opts) => add(opts, &sys_conf, &env),
        Del(opts) => del(opts, &sys_conf, &env),
        Dump(opts) => dump(opts, &sys_conf),
        Search(opts) => find(opts, &sys_conf, &env),
        Check(opts) => check(opts, &sys_conf),
    }
}

fn clear(_: ClearOpts, _: &cfg::All, env: &Environment) {
    if let Ok(db) = env.open_db(Some("trust.db")) {
        let mut tx = env.begin_rw_txn().expect("failed to start db transaction");
        tx.clear_db(db).expect("failed to force clear db");
        tx.commit().expect("failed to commit force clear db");
    }
}

fn init(opts: InitOpts, cfg: &cfg::All, env: &Environment) {
    if opts.force {
        clear(ClearOpts {}, cfg, env)
    }

    let db = env
        .create_db(Some("trust.db"), DatabaseFlags::DUP_SORT)
        .expect("failed to create db");

    if opts.empty {
        return;
    }

    let t = SystemTime::now();
    let sys = if opts.dpkg {
        load_dpkg_trust().expect("failed to load dpkg trust")
    } else {
        load_rpm_trust(&cfg.system.system_trust_path).expect("failed to load rpm trust")
    };

    let mut tx = env.begin_rw_txn().expect("failed to start db transaction");
    for trust in &sys {
        let v = format!("{} {} {}", 1, trust.size, trust.hash);
        match tx.put(db, &trust.path, &v, WriteFlags::APPEND_DUP) {
            Ok(_) => {}
            Err(_) => println!("skipped {}", trust.path),
        }
    }
    tx.commit().expect("failed to commit db transaction");

    let duration = t.elapsed().expect("timer failure");
    println!(
        "initialized db with {} entries in {} seconds",
        sys.len(),
        duration.as_secs()
    );
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

fn del(opts: DelRecOpts, _: &cfg::All, env: &Environment) {
    let db = env.open_db(Some("trust.db")).expect("failed to open db");
    let mut tx = env.begin_rw_txn().expect("failed to start db transaction");
    tx.del(db, &opts.path, None)
        .expect("failed to delete record");
    tx.commit().expect("failed to commit db transaction")
}

fn find(opts: SearchDbOpts, _: &cfg::All, env: &Environment) {
    let db = env.open_db(Some("trust.db")).expect("failed to open db");
    let tx = env.begin_ro_txn().expect("failed to start ro tx");
    match tx.get(db, &opts.key) {
        Ok(e) => {
            println!(
                "{}",
                String::from_utf8(Vec::from(e)).expect("failed to read string")
            )
        }
        Err(_) => {
            println!("entry not found")
        }
    }
}

fn dump(opts: DumpDbOpts, cfg: &cfg::All) {
    let db = read::load_trust_db(&cfg.system.trust_db_path).expect("failed to load db");
    match opts.outfile {
        None => db
            .iter()
            .for_each(|(k, v)| println!("{} {} {}", k, v.trusted.size, v.trusted.hash)),
        Some(path) => {
            let mut f = File::create(&path).expect("unable to create file");
            for (k, v) in db.iter() {
                f.write_all(format!("{} {} {}\n", k, v.trusted.size, v.trusted.hash).as_bytes())
                    .expect("failed to write entry");
            }
        }
    }
}

fn check(_: CheckDbOpts, cfg: &cfg::All) {
    let db = read::load_trust_db(&cfg.system.trust_db_path).expect("failed to load db");

    let t = SystemTime::now();
    let count = check_trust_db(&db)
        .unwrap()
        .iter()
        .filter(|(_, v)| v.status.is_some())
        .count();

    let duration = t.elapsed().expect("timer failure");
    println!(
        "checked {} entries in {} seconds",
        count,
        duration.as_secs()
    );
}

fn new_trust_record(path: &str) -> Result<Trust, Error> {
    if Path::new(path).is_dir() {
        return Err(DirTrustError);
    }

    let f = File::open(path)?;
    let sha = sha256_digest(BufReader::new(&f))?;

    Ok(Trust {
        path: path.to_string(),
        size: f.metadata().unwrap().len(),
        hash: sha,
    })
}

fn load_dpkg_trust() -> Result<Vec<Trust>, Error> {
    // check that dpkg-query exists and can be called
    let _exists = Command::new("dpkg-query")
        .arg("--version")
        .output()
        .map_err(|_| DpkgNotFound)?;

    let packages: Vec<String> = Command::new("dpkg-query")
        .arg("-l")
        .output()
        .map_err(DpkgCommandFail)
        .map(output_lines)?
        .iter()
        .flatten()
        .skip(6)
        .flat_map(|s| s.split_whitespace().nth(1))
        .map(String::from)
        .collect();

    let files: Vec<String> = packages
        .par_iter()
        .flat_map(|p| Command::new("dpkg-query").args(vec!["-L", p]).output())
        .flat_map(output_lines)
        .flatten()
        .collect();

    Ok(files
        .iter()
        .filter_map(|s| match new_trust_record(s) {
            Ok(t) => Some(t),
            Err(_) => None,
        })
        .collect())
}

fn output_lines(out: Output) -> Result<Vec<String>, Error> {
    Ok(String::from_utf8(out.stdout)?
        .lines()
        .map(String::from)
        .collect())
}
