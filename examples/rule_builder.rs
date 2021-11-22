use clap::Clap;
use fapolicy_rules::{Decision, Object, Permission, Rule, Subject};

#[derive(Clap)]
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
