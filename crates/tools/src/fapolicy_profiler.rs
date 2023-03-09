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
use fapolicy_daemon::profiler::Profiler;
use fapolicy_rules::read::load_rules_db;
use std::error::Error;
use std::os::unix::prelude::CommandExt;
use std::path::PathBuf;
use std::process::Command;

#[derive(Parser)]
#[clap(name = "File Access Policy Profiler", version = "v0.0.0")]
struct Opts {
    /// path to *.rules or rules.d
    #[clap(short, long)]
    rules: Option<String>,

    /// out path for daemon stdout log
    #[clap(long)]
    stdout: Option<String>,

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
    let opts: Opts = Opts::parse();
    log::info!("profiling: {:?}", opts.target);
    let target = opts.target.first().expect("target not specified");
    let args: Vec<&String> = opts.target.iter().skip(1).collect();

    let mut profiler = Profiler::new();
    let db = opts
        .rules
        .map(|p| load_rules_db(&p).expect("failed to load rules"));

    if let Some(path) = opts.stdout.map(PathBuf::from) {
        if path.exists() {
            log::warn!("deleting existing log file from {}", path.display());
            std::fs::remove_file(&path)?;
        }
        profiler.events_log = Some(path);
    }

    profiler.activate_with_rules(db.as_ref())?;
    let mut cmd = Command::new(target);
    if let Some(uid) = opts.uid {
        cmd.uid(uid);
    }
    if let Some(gid) = opts.gid {
        cmd.gid(gid);
    }
    let out = cmd.args(args).output()?;
    println!("{}", String::from_utf8(out.stdout)?);
    profiler.deactivate()?;

    Ok(())
}
