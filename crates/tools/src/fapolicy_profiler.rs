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

use clap::Parser;
use fapolicy_daemon::fapolicyd::START_POLLING_EVENTS_MESSAGE;
use fapolicy_daemon::profiler::Profiler;
use fapolicy_rules::read::load_rules_db;
use std::error::Error;
use std::fs::File;
use std::io::{BufRead, BufReader, Write};
use std::os::unix::prelude::CommandExt;
use std::path::PathBuf;
use std::process::Command;
use strip_ansi_escapes::strip_str;

#[derive(Parser)]
#[clap(name = "File Access Policy Profiler", version = "v0.0.0")]
struct Opts {
    /// do not write events to stdout
    #[clap(long)]
    quiet: bool,

    /// path to *.rules or rules.d
    #[clap(long)]
    rules: Option<String>,

    /// path to write daemon log
    #[clap(long)]
    dlog: Option<String>,

    /// path to write command log
    #[clap(long)]
    clog: Option<String>,

    /// the profiling uid
    #[clap(long)]
    uid: Option<u32>,

    /// the profiling gid
    #[clap(long)]
    gid: Option<u32>,

    /// the literal target to run, prefix by double hyphens
    /// faprofiler -- ls -al /tmp
    #[clap(required = true, allow_hyphen_values = true)]
    target: Vec<String>,
}

fn main() -> Result<(), Box<dyn Error>> {
    fapolicy_tools::setup_human_panic();
    env_logger::init();

    let opts: Opts = Opts::parse();
    log::info!("profiling: {:?}", opts.target);
    let target = opts.target.first().expect("target not specified");
    let args: Vec<&String> = opts.target.iter().skip(1).collect();
    let mut profiler = Profiler::new();
    let db = opts
        .rules
        .map(|p| load_rules_db(&p).expect("failed to load rules"));
    if let Some(path) = opts.dlog.as_ref().map(PathBuf::from) {
        if path.exists() {
            log::warn!("deleting existing log file from {}", path.display());
            std::fs::remove_file(&path)?;
        }
        profiler.events_log = Some(path);
    }

    let outfile = profiler.activate_with_rules(db.as_ref())?;
    let mut cmd = Command::new(target);
    if let Some(uid) = opts.uid {
        cmd.uid(uid);
    }
    if let Some(gid) = opts.gid {
        cmd.gid(gid);
    }

    let out = cmd.args(args).output()?;
    profiler.deactivate()?;

    // write command output to file if specified
    if let Some(path) = opts.clog.map(PathBuf::from) {
        let mut f = File::create(&path)?;
        f.write_all(&out.stdout)?;
        log::info!("wrote cmd output to {}", path.display());
    }

    // if the events file was not specified we will dump to the screen
    if !opts.quiet {
        let f = File::open(outfile)?;
        let bufrdr = BufReader::new(&f);
        let lines = bufrdr.lines().map(|x| x.unwrap());
        for line in lines
            .skip_while(|l| !l.contains(START_POLLING_EVENTS_MESSAGE))
            .skip(1)
        {
            if strip_str(&line).contains("[ INFO ]") {
                if let Some((_, rhs)) = line.split_once("]: ") {
                    println!("{rhs}");
                } else {
                    log::warn!("failed to split output line \"{}\", ignoring", line);
                }
            }
        }
    }

    if let Some(path) = opts.dlog.map(PathBuf::from) {
        log::info!("wrote daemon output to {}", path.display());
    }

    Ok(())
}
