use clap::Clap;

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

    let sys = fapolicy_analyzer::sys::System::boot(fapolicy_analyzer::sys::SystemCfg {
        ancillary_trust_path: opts.db,
    });

    println!("Loaded {} trust records", sys.trust.len())
}
