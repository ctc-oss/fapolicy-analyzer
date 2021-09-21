use clap::Clap;

use crate::Error::{DirTrustError, DpkgCommandFail, DpkgNotFound};
use crate::Subcommand::{AddRec, DelRec, Dump, Init, Search};
use fapolicy_api::trust::Trust;
use fapolicy_app::cfg;
use fapolicy_daemon::rpm::load_system_trust as load_rpm_trust;
use fapolicy_trust::read;
use fapolicy_util::sha::sha256_digest;
use lmdb::{DatabaseFlags, Environment, Transaction, WriteFlags};
use std::fs::File;
use std::io;
use std::io::BufReader;
use std::path::Path;
use std::process::{Command, Output};
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

    /// overwrite existing database
    #[clap(long)]
    force: bool,

    /// use dpkg to generate db
    #[clap(long)]
    dpkg: bool,
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

    println!("opening trust db at {}", trust_db_path.to_string_lossy());
    let env = Environment::new()
        .set_max_dbs(1)
        .set_map_size(104857600)
        .open(trust_db_path)
        .expect("unable to open path to trust db");

    match all_opts.cmd {
        Init(opts) => init(opts, &sys_conf, &env),
        AddRec(opts) => add(opts, &sys_conf, &env),
        DelRec(_) => {}
        Dump(opts) => dump(opts, &sys_conf),
        Search(_) => {}
    }
}

fn init(opts: InitOpts, cfg: &cfg::All, env: &Environment) {
    if opts.force {
        if let Some(db) = env.open_db(Some("trust.db")).ok() {
            let mut tx = env.begin_rw_txn().expect("failed to start db transaction");
            tx.clear_db(db).expect("failed to force clear db");
            tx.commit();
        }
    }

    let db = env
        .create_db(Some("trust.db"), DatabaseFlags::DUP_SORT)
        .expect("failed to create db");

    if opts.empty {
        return;
    }

    let sys = if opts.dpkg {
        load_dpkg_trust().expect("failed to load dpkg trust")
    } else {
        load_rpm_trust(&cfg.system.system_trust_path).expect("failed to load rpm trust")
    };

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
        .map_err(|e| DpkgCommandFail(e))
        .map(|x| output_lines(x))?
        .iter()
        .flatten()
        .skip(6)
        .flat_map(|s| s.split_whitespace().nth(1))
        .map(|s| s.to_string())
        .collect();

    let files: Vec<String> = packages
        .iter()
        .take(50)
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
        .map(|s| s.to_string())
        .collect())
}
