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

use clap::Clap;
use fapolicy_daemon::profiler::Profiler;
use fapolicy_rules::read::load_rules_db;
use std::error::Error;
use std::path::PathBuf;
use std::process::Command;

#[derive(Clap)]
#[clap(name = "File Access Policy Profiler", version = "v0.0.0")]
struct Opts {
    /// path to *.rules or rules.d
    #[clap(short, long)]
    rules: Option<String>,

    /// out path for daemon stdout log
    #[clap(long)]
    stdout: Option<String>,

    /// the literal target to run, prefix by double hyphens
    /// faprofiler -- ls -al /tmp
    #[clap(required = true, allow_hyphen_values = true)]
    target: Vec<String>,
}

fn main() -> Result<(), Box<dyn Error>> {
    let opts: Opts = Opts::parse();
    eprintln!("profiling: {:?}", opts.target);
    let target = opts.target.first().expect("target not specified");
    let args: Vec<&String> = opts.target.iter().skip(1).collect();

    let mut profiler = Profiler::new();
    let db = opts
        .rules
        .map(|p| load_rules_db(&p).expect("failed to load rules"));

    if let Some(path) = opts.stdout.map(PathBuf::from) {
        if path.exists() {
            eprintln!(
                "warning: deleting existing log file from {}",
                path.display()
            );
            std::fs::remove_file(&path)?;
        }
        profiler.stdout_log = Some(path);
    }

    profiler.activate_with_rules(db.as_ref())?;
    let out = Command::new(target).args(args).output()?;
    println!("{}", String::from_utf8(out.stdout)?);
    profiler.deactivate()?;

    Ok(())
}
