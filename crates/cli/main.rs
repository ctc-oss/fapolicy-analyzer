use clap::Clap;

use fapolicyd::trust::FileTrustDB;

#[derive(Clap)]
#[clap(version = "v0.2.0")]
/// File Access Policy Analyzer
struct Opts {
    /// path to ancillary trust database
    #[clap(long, default_value = "/etc/fapolicyd/fapolicyd.trust")]
    db: String,
}

fn main() {
    let opts: Opts = Opts::parse();

    let sys = core::System::boot(core::SystemCfg {
        ancillary_trust_path: opts.db,
    });
}
