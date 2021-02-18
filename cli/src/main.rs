use clap::Clap;

use fapolicy_analyzer::{svc, sys};

mod cmd;

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
    /// path to ancillary trust database (file)
    #[clap(long)]
    file: Option<String>,

    /// path to fapolicyd trust database (lmdb)
    #[clap(long)]
    db: Option<String>,

    /// path to system trust database (rpm)
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
        SubCommands::Trust(trust_opts) => {
            let sys = sys::System::boot(sys::SystemCfg {
                trust_db_path: trust_opts.db,
                system_trust_path: trust_opts.rpmdb,
                ancillary_trust_path: trust_opts.file,
            });

            println!(
                "Loaded {}: system / {}: fapolicyd trust records",
                sys.system_trust.len(),
                sys.ancillary_trust.len()
            );
            //
            // // check
            // for f in t {
            //     let meta = fs::metadata(&f.path).unwrap();
            //     let sz = meta.len();
            //     if sz != f.size {
            //         println!("{} wrong size {}, expected {}", f.path, f.size, sz);
            //     }
            // }
        }
        SubCommands::Daemon(opts) => {
            let daemon = svc::Daemon::new("fapolicyd.service");
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
