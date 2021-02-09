use clap::Clap;

#[derive(Clap)]
#[clap(version = "v0.2.0")]
/// File Access Policy Analyzer
struct Opts {
    /// path to ancillary trust database
    #[clap(long, default_value = "/etc/fapolicyd/fapolicyd.trust")]
    trustdb: String,

    /// path to system trust database
    #[clap(long)]
    rpmdb: Option<String>,
}

fn main() {
    let opts: Opts = Opts::parse();

    let sys = fapolicy_analyzer::sys::System::boot(fapolicy_analyzer::sys::SystemCfg {
        system_trust_path: opts.rpmdb,
        ancillary_trust_path: opts.trustdb,
    });

    println!("Loaded {} trust records", sys.trust.len())
}
