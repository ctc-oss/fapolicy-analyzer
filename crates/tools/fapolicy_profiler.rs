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
use std::process::Command;

#[derive(Clap)]
#[clap(name = "File Access Policy Profiler", version = "v0.0.0")]
struct Opts {
    /// path to *.rules or rules.d
    rules_path: Option<String>,
}

fn main() -> Result<(), Box<dyn Error>> {
    let opts: Opts = Opts::parse();
    let mut profiler = Profiler::new();
    let db = if let Some(rules_path) = opts.rules_path {
        Some(load_rules_db(&rules_path)?)
    } else {
        None
    };

    profiler.activate_with_rules(db.as_ref())?;
    let out = Command::new("cat")
        .arg("/etc/fapolicyd/compiled.rules")
        .output()?;
    println!("{}", String::from_utf8(out.stdout)?);
    profiler.deactivate()?;

    Ok(())
}
