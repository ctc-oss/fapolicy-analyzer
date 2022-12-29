// Copyright Concurrent Technologies Corporation 2021
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

use std::fs::File;
use std::io;
use std::io::{BufReader, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::time::SystemTime;

use clap::Parser;
use lmdb::{Cursor, DatabaseFlags, Environment, Transaction, WriteFlags};
use rayon::prelude::*;
use thiserror::Error;

use fapolicy_app::cfg;
use fapolicy_daemon::fapolicyd::TRUST_LMDB_NAME;
use fapolicy_trust::load::keep_entry;
use fapolicy_trust::read::rpm_trust;
use fapolicy_trust::stat::Status::{Discrepancy, Missing, Trusted};
use fapolicy_trust::{check, load, parse, read, Trust};
use fapolicy_util::sha::sha256_digest;

use crate::Error::{DirTrustError, DpkgCommandFail, DpkgNotFound};
use crate::Subcommand::{Add, Check, Clear, Count, Del, Dump, Init, Load, Search};

/// An Error that can occur in this app
#[derive(Error, Debug)]
pub enum Error {
    #[error("dpkg-query not found on path")]
    DpkgNotFound,

    #[error("dpkg-query command failed, {0}")]
    DpkgCommandFail(io::Error),

    #[error("{0}")]
    RpmError(#[from] fapolicy_util::rpm::Error),

    #[error("{0}")]
    LmdbError(#[from] lmdb::Error),

    #[error("{0}")]
    TrustError(#[from] fapolicy_trust::error::Error),

    #[error("{0}")]
    AppError(#[from] fapolicy_app::error::Error),

    #[error("cant trust a directory")]
    DirTrustError,

    #[error("file io error, {0}")]
    FileError(#[from] io::Error),

    #[error("file hashing error, {0}")]
    HashError(#[from] fapolicy_util::sha::Error),

    #[error("error reading stdout")]
    ParseError(#[from] std::string::FromUtf8Error),
}

#[derive(Parser)]
#[clap(name = "Trust DB Utils", version = "v0.1")]
struct Opts {
    #[clap(subcommand)]
    cmd: Subcommand,

    /// Verbose output
    #[clap(short, long)]
    verbose: bool,

    /// The fapolicyd database directory
    /// Defaults to XDG conf value
    dbdir: Option<String>,
}

#[derive(Parser)]
enum Subcommand {
    /// Clear the trust database of all entries
    Clear(ClearOpts),
    /// Initialize the trust database from system trust
    Init(InitOpts),
    /// Add a file to the trust database
    Add(AddRecOpts),
    /// Remove a file from the trust database
    Del(DelRecOpts),
    /// Dump all trust entries to file or stdout
    Dump(DumpDbOpts),
    /// Search for a trust entry
    Search(SearchDbOpts),
    /// Check trust status
    Check(CheckDbOpts),
    /// Count the number of trust entries
    Count(CountOpts),
    /// Load file trust entries
    Load(LoadOpts),
}

#[derive(Parser)]
struct ClearOpts {}

#[derive(Parser)]
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

#[derive(Parser)]
struct AddRecOpts {
    /// File to add
    path: String,
}

#[derive(Parser)]
struct DelRecOpts {
    /// File to delete
    path: String,
}

#[derive(Parser)]
struct DumpDbOpts {
    /// Optional file
    #[clap(short, long)]
    outfile: Option<String>,
}

#[derive(Parser)]
struct SearchDbOpts {
    /// File to delete
    #[clap(long)]
    key: String,
}

#[derive(Parser)]
struct CheckDbOpts {
    /// use par_iter
    #[clap(long)]
    par: bool,
}

#[derive(Parser)]
struct LoadOpts {
    /// File trust source
    path: String,
}

#[derive(Parser)]
struct CountOpts {}

fn main() -> Result<(), Error> {
    let sys_conf = cfg::All::load()?;
    let all_opts: Opts = Opts::parse();
    let trust_db_path = match all_opts.dbdir {
        Some(ref p) => Path::new(p),
        None => Path::new(&sys_conf.system.trust_lmdb_path),
    };

    if !trust_db_path.exists() {
        panic!("dbdir does not exist")
    } else if !trust_db_path.is_dir() {
        panic!("dbdir must be a directory")
    }

    if all_opts.verbose {
        println!("opening trust db at {}", trust_db_path.to_string_lossy());
    }

    let env = Environment::new()
        .set_max_dbs(1)
        .set_map_size(104857600)
        .open(trust_db_path)?;

    match all_opts.cmd {
        Clear(opts) => clear(opts, &sys_conf, &env),
        Init(opts) => init(opts, all_opts.verbose, &sys_conf, &env),
        Add(opts) => add(opts, &sys_conf, &env),
        Del(opts) => del(opts, &sys_conf, &env),
        Dump(opts) => dump(opts, &sys_conf),
        Search(opts) => find(opts, &sys_conf, &env),
        Check(opts) => check(opts, &sys_conf),
        Count(opts) => count(opts, &sys_conf, &env),
        Load(opts) => load(opts, all_opts.verbose, &sys_conf, &env),
    }
}

fn clear(_: ClearOpts, _: &cfg::All, env: &Environment) -> Result<(), Error> {
    if let Ok(db) = env.open_db(Some(TRUST_LMDB_NAME)) {
        let mut tx = env.begin_rw_txn()?;
        tx.clear_db(db)?;
        tx.commit()?;
    };

    Ok(())
}

fn init(opts: InitOpts, verbose: bool, cfg: &cfg::All, env: &Environment) -> Result<(), Error> {
    if opts.force {
        clear(ClearOpts {}, cfg, env)?;
    }

    let db = env.create_db(Some(TRUST_LMDB_NAME), DatabaseFlags::DUP_SORT)?;

    if opts.empty {
        return Ok(());
    }

    let t = SystemTime::now();
    let sys = if opts.dpkg {
        dpkg_trust()?
    } else {
        rpm_trust(&PathBuf::from(&cfg.system.system_trust_path))?
    };

    let sys = if let Some(c) = opts.count {
        let mut m = sys;
        m.truncate(c);
        m
    } else {
        sys
    };

    let mut tx = env.begin_rw_txn()?;
    let mut skipped = 0;
    for trust in &sys {
        let v = format!("{} {} {}", 1, trust.size, trust.hash);
        match tx.put(db, &trust.path, &v, WriteFlags::APPEND_DUP) {
            Ok(_) => {}
            Err(e) => {
                skipped += 1;
                if verbose {
                    println!("skipped {} {:?}", trust.path, e);
                }
            }
        }
    }
    tx.commit()?;

    let duration = t.elapsed().expect("timer failure");

    if verbose {
        println!(
            "initialized db with {} entries in {} seconds ({} skipped)",
            sys.len() - skipped,
            duration.as_secs(),
            skipped
        );
    }

    Ok(())
}

fn load(opts: LoadOpts, verbose: bool, _: &cfg::All, env: &Environment) -> Result<(), Error> {
    let source = match PathBuf::from(&opts.path) {
        source if source.is_dir() => read::from_dir(&source)?,
        source => read::from_file(&source)?,
    };

    let source: Result<Vec<(String, Trust)>, fapolicy_trust::error::Error> = source
        .iter()
        .map(|(o, r)| parse::trust_record(r).map(|t| (o.display().to_string(), t)))
        .collect();

    //need to parse the source entries out into Trust structs

    let db = env.open_db(Some(TRUST_LMDB_NAME))?;
    let mut tx = env.begin_rw_txn()?;
    for (o, t) in source? {
        let v = format!("{} {} {}", 2, t.size, t.hash);
        tx.put(db, &t.path, &v, WriteFlags::APPEND_DUP)?;
        if verbose {
            println!("{} {}", o, t);
        }
    }
    tx.commit()?;

    Ok(())
}

fn add(opts: AddRecOpts, _: &cfg::All, env: &Environment) -> Result<(), Error> {
    let trust = new_trust_record(&opts.path)?;
    let db = env.open_db(Some(TRUST_LMDB_NAME))?;
    let mut tx = env.begin_rw_txn()?;
    let v = format!("{} {} {}", 2, trust.size, trust.hash);
    tx.put(db, &trust.path, &v, WriteFlags::APPEND_DUP)?;
    tx.commit()?;

    Ok(())
}

fn del(opts: DelRecOpts, _: &cfg::All, env: &Environment) -> Result<(), Error> {
    let db = env.open_db(Some(TRUST_LMDB_NAME))?;
    let mut tx = env.begin_rw_txn()?;
    tx.del(db, &opts.path, None)?;
    tx.commit()?;

    Ok(())
}

fn find(opts: SearchDbOpts, _: &cfg::All, env: &Environment) -> Result<(), Error> {
    let db = env.open_db(Some(TRUST_LMDB_NAME))?;
    let tx = env.begin_ro_txn()?;
    match tx.get(db, &opts.key) {
        Ok(e) => println!("{}", String::from_utf8(Vec::from(e))?),
        Err(_) => println!("entry not found"),
    };

    Ok(())
}

fn dump(opts: DumpDbOpts, cfg: &cfg::All) -> Result<(), Error> {
    let db = load::trust_db(
        &PathBuf::from(&cfg.system.trust_lmdb_path),
        &PathBuf::from(&cfg.system.trust_dir_path),
        Some(&PathBuf::from(&cfg.system.trust_file_path)),
    )?;
    match opts.outfile {
        None => {
            for (_, v) in db.iter() {
                println!("{}", v.trusted)
            }
        }
        Some(path) => {
            let mut f = File::create(&path)?;
            for (_, v) in db.iter() {
                f.write_all(format!("{}\n", v.trusted).as_bytes())?;
            }
        }
    };

    Ok(())
}

fn check(_: CheckDbOpts, cfg: &cfg::All) -> Result<(), Error> {
    let db = load::trust_db(
        &PathBuf::from(&cfg.system.trust_lmdb_path),
        &PathBuf::from(&cfg.system.trust_dir_path),
        Some(&PathBuf::from(&cfg.system.trust_file_path)),
    )?;

    let t = SystemTime::now();
    let db = check::disk_sync(&db)?;
    let duration = t.elapsed().expect("timer failure");

    for (_, v) in db.iter() {
        match &v.status {
            Some(Missing(t)) => println!("missing: {}", t.path),
            Some(Discrepancy(t, _)) => println!("mismatch: {}", t.path),
            Some(Trusted(_, _)) => {}
            None => {}
        }
    }

    let count = db.iter().count();
    println!(
        "checked {} entries in {} seconds",
        count,
        duration.as_secs()
    );

    Ok(())
}

fn count(_: CountOpts, _: &cfg::All, env: &Environment) -> Result<(), Error> {
    let db = env.open_db(Some(TRUST_LMDB_NAME))?;
    let tx = env.begin_ro_txn()?;
    let mut c = tx.open_ro_cursor(db)?;
    let cnt = c.iter().count();
    println!("{}", cnt);

    Ok(())
}

fn new_trust_record(path: &str) -> Result<Trust, Error> {
    if Path::new(path).is_dir() {
        return Err(DirTrustError);
    }

    let f = File::open(path)?;
    let sha = sha256_digest(BufReader::new(&f))?;

    Ok(Trust {
        path: path.to_string(),
        size: f.metadata()?.len(),
        hash: sha,
    })
}

// number of lines to eliminate the `dpkg-query -l` header
const DPKG_QUERY_HEADER_LINES: usize = 6;
const DPKG_QUERY: &str = "dpkg-query";
fn dpkg_trust() -> Result<Vec<Trust>, Error> {
    // check that dpkg-query exists and can be called
    let _exists = Command::new(DPKG_QUERY)
        .arg("--version")
        .output()
        .map_err(|_| DpkgNotFound)?;

    let packages: Vec<String> = Command::new(DPKG_QUERY)
        .arg("-l")
        .output()
        .map_err(DpkgCommandFail)
        .map(output_lines)?
        .iter()
        .flatten()
        .skip(DPKG_QUERY_HEADER_LINES)
        .flat_map(|s| s.split_whitespace().nth(1))
        .map(String::from)
        .collect();

    Ok(packages
        .par_iter()
        .flat_map(|p| Command::new(DPKG_QUERY).args(vec!["-L", p]).output())
        .flat_map(output_lines)
        .flatten()
        // apply the rpm filter to limit results
        .filter(|p| keep_entry(p))
        .filter_map(|s| match new_trust_record(&s) {
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
