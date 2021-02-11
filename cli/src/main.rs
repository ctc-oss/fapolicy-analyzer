use clap::Clap;
use fapolicy_analyzer::svc::Daemon;

#[derive(Clap)]
#[clap(version = "0.0.1")]
/// File Access Policy Analyzer
struct Opts {
    #[clap(subcommand)]
    subcmd: SubCommands,
}

#[derive(Clap)]
enum SubCommands {
    /// fapolicyd service commands
    #[clap(version = "0.0.1")]
    Daemon(DaemonOpts),
    Trust(TrustOpts),
}

/// Trust commands
#[derive(Clap)]
struct TrustOpts {
    /// path to ancillary trust database
    #[clap(long)]
    trustdb: Option<String>,

    /// path to system trust database
    #[clap(long)]
    rpmdb: Option<String>,
}

/// Daemon commands
#[derive(Clap)]
struct DaemonOpts {
    #[clap(subcommand)]
    subcmd: DaemonSubCommands,
}

#[derive(Clap)]
enum DaemonSubCommands {
    Start(DaemonSubOpts),
    Stop(DaemonSubOpts),
    Enable(DaemonSubOpts),
    Disable(DaemonSubOpts),
}

/// A subcommand for controlling testing
#[derive(Clap)]
struct DaemonSubOpts {}

fn main() {
    let cli: Opts = Opts::parse();
    match cli.subcmd {
        SubCommands::Trust(opts) => {
            let sys = fapolicy_analyzer::sys::System::boot(fapolicy_analyzer::sys::SystemCfg {
                system_trust_path: opts.rpmdb,
                ancillary_trust_path: opts.trustdb,
            });

            println!("Loaded {} trust records", sys.trust.len())
        }
        SubCommands::Daemon(opts) => {
            let daemon = Daemon::new("notfapolicyd.service");
            match opts.subcmd {
                DaemonSubCommands::Start(_) => {
                    println!("daemon start");
                    daemon.start().unwrap();
                }
                DaemonSubCommands::Stop(_) => {
                    println!("daemon stop");
                    daemon.stop().unwrap();
                }
                DaemonSubCommands::Enable(_) => {
                    println!("daemon enable");
                    daemon.enable().unwrap();
                }
                DaemonSubCommands::Disable(_) => {
                    println!("daemon disable");
                    daemon.disable().unwrap();
                }
            }
            println!("daemon command")
        }
    }
}
