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

use fapolicy_rules::{Decision, Object, Permission, Rule, Subject};

#[derive(Parser)]
#[clap(name = "Rule Builder")]
/// Typesafe Rule Building CLI
struct Opts {
    /// Subject
    #[clap(long, default_value = "all")]
    subj: Subject,

    /// Permission
    #[clap(long, default_value = "perm=any")]
    perm: Permission,

    /// Object
    #[clap(long, default_value = "all")]
    obj: Object,

    /// Decision
    #[clap(long, default_value = "deny_audit")]
    dec: Decision,
}

fn main() {
    let opts: Opts = Opts::parse();
    let rule = Rule {
        subj: opts.subj,
        perm: opts.perm,
        obj: opts.obj,
        dec: opts.dec,
    };

    println!("{}", rule);
}
