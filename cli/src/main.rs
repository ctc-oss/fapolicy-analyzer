use std::io::Write;

use clap::Clap;
use std::fs::OpenOptions;

use fapolicy_analyzer::{svc, sys, trust};

#[derive(Clap)]
#[clap(version = "0.0.3")]
/// File Access Policy Analyzer
struct Opts {
    #[clap(subcommand)]
    subcmd: SubCommands,
}

#[derive(Clap)]
enum SubCommands {
    /// fapolicyd service commands
    #[clap(version = "0.0.3")]
    Daemon(DaemonOpts),
    Trust(TrustOpts),
}

/// Trust commands
#[derive(Clap)]
struct TrustOpts {
    /// path to fapolicyd trust database (lmdb)
    #[clap(long)]
    db: Option<String>,

    /// path to system trust database (rpm)
    #[clap(long)]
    rpmdb: Option<String>,

    #[clap(subcommand)]
    cmd: TrustSubCommands,
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

#[derive(Clap)]
enum TrustSubCommands {
    List(TrustSubOpts),
    Add(TrustAddOpts),
}

#[derive(Clap)]
struct DaemonSubOpts {}

#[derive(Clap)]
struct TrustSubOpts {
    /// path to ancillary trust database (file)
    #[clap(long)]
    file: Option<String>,
}

#[derive(Clap)]
struct TrustAddOpts {
    /// path to ancillary trust database (file)
    #[clap(short, long)]
    file: Option<String>,

    hash: String,
    path: String,
}

fn main() {
    let cli: Opts = Opts::parse();
    match cli.subcmd {
        SubCommands::Trust(trust_opts) => match trust_opts.cmd {
            TrustSubCommands::List(subopts) => {
                let sys = sys::System::boot(sys::SystemCfg {
                    trust_db_path: trust_opts.db,
                    system_trust_path: trust_opts.rpmdb,
                    ancillary_trust_path: subopts.file,
                });

                println!(
                    "Loaded {}: db / {}: system / {}: file records",
                    sys.trust_db.len(),
                    sys.system_trust.len(),
                    sys.ancillary_trust.len()
                );
            }
            TrustSubCommands::Add(add_op_opts) => {
                let t = trust::new_trust_record(&add_op_opts.path, &add_op_opts.hash).unwrap();
                let mut file = OpenOptions::new()
                    .write(true)
                    .append(true)
                    .create(true)
                    .open(add_op_opts.file.unwrap())
                    .unwrap();

                file.write_all(format!("{} {} {}\n", t.path, t.size, t.hash).as_bytes())
                    .unwrap()
            }
        },
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
