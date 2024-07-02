/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

// todo;; tracking the fapolicyd specific bits in here to determine if bindings are worthwhile

use crate::error::Error;
use std::fs::File;
use std::io::Read;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::time::Duration;
use std::{io, thread};

pub const TRUST_LMDB_PATH: &str = "/var/lib/fapolicyd";
pub const TRUST_LMDB_NAME: &str = "trust.db";
pub const TRUST_DIR_PATH: &str = "/etc/fapolicyd/trust.d";
pub const TRUST_FILE_PATH: &str = "/etc/fapolicyd/fapolicyd.trust";
pub const RULES_FILE_PATH: &str = "/etc/fapolicyd/rules.d";
pub const COMPILED_RULES_PATH: &str = "/etc/fapolicyd/compiled.rules";
pub const CONFIG_FILE_PATH: &str = "/etc/fapolicyd/fapolicyd.conf";
pub const TRUST_FILTER_FILE_PATH: &str = "/etc/fapolicyd/fapolicyd-filter.conf";
pub const RPM_DB_PATH: &str = "/var/lib/rpm";
pub const FIFO_PIPE: &str = "/run/fapolicyd/fapolicyd.fifo";
pub const START_POLLING_EVENTS_MESSAGE: &str = "Starting to listen for events";

#[derive(Clone, Debug)]
pub enum Version {
    Unknown,
    Release { major: u8, minor: u8, patch: u8 },
}

/// A fapolicyd runner
pub struct Daemon {
    pub name: String,
    alive: Arc<AtomicBool>,
    term: Arc<AtomicBool>,
}

impl Daemon {
    pub fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
            alive: Default::default(),
            term: Default::default(),
        }
    }

    pub fn active(&self) -> bool {
        self.alive.load(Ordering::Relaxed)
    }

    pub fn stop(&self) {
        self.term.store(true, Ordering::Relaxed)
    }

    pub fn start(&self, events_log: Option<&PathBuf>) -> io::Result<()> {
        let (mut cmd, _) = build(
            "/usr/sbin/fapolicyd --debug --permissive --no-details",
            events_log,
        );
        let alive: Arc<AtomicBool> = self.alive.clone();
        let term: Arc<AtomicBool> = self.term.clone();

        thread::spawn(move || {
            let mut execd = Execd::new(cmd.spawn().unwrap());

            // the process is now alive
            alive.store(true, Ordering::Relaxed);

            while let Ok(true) = execd.running() {
                thread::sleep(Duration::from_secs(1));
                if term.load(Ordering::Relaxed) {
                    execd.kill().expect("kill daemon");
                    break;
                }
            }

            // we need to wait on the process to die, instead of just blocking
            // this loop provides the ability to add a harder stop impl, abort
            term.store(false, Ordering::Relaxed);
            while let Ok(true) = execd.running() {
                if term.load(Ordering::Relaxed) {
                    execd.kill().expect("abort daemon");
                    break;
                }
                thread::sleep(Duration::from_secs(1));
            }

            // no longer alive
            alive.store(false, Ordering::Relaxed);
        });

        Ok(())
    }
}

type CmdArgs = (Command, String);
fn build(args: &str, out: Option<&PathBuf>) -> CmdArgs {
    let opts: Vec<&str> = args.split(' ').collect();
    let (target, opts) = opts.split_first().expect("invalid cmd string");

    let mut cmd = Command::new(target);

    if let Some(path) = out {
        let f = File::create(path).unwrap();
        cmd.stderr(Stdio::from(f));
    }

    cmd.args(opts);
    (cmd, args.to_string())
}

/// Internal struct used to inspect a running process
struct Execd {
    proc: Option<Child>,
}

impl Execd {
    fn new(proc: Child) -> Execd {
        Execd { proc: Some(proc) }
    }

    /// Is process is still running?, never blocks
    fn running(&mut self) -> io::Result<bool> {
        match self.proc.as_mut().unwrap().try_wait() {
            Ok(Some(_)) => Ok(false),
            Ok(None) => Ok(true),
            Err(e) => Err(e),
        }
    }

    /// Cancel the process, without blocking
    fn kill(&mut self) -> io::Result<()> {
        self.proc.as_mut().unwrap().kill()
    }
}

/// watch a fapolicyd log at the specified path for the
/// message it prints when ready to start polling events
pub fn wait_until_ready(path: &Path) -> Result<(), Error> {
    let mut f = File::open(path)?;
    for _ in 0..10 {
        thread::sleep(Duration::from_secs(1));
        let mut s = String::new();
        f.read_to_string(&mut s)?;
        if s.contains(START_POLLING_EVENTS_MESSAGE) {
            return Ok(());
        }
    }
    Err(Error::NotReady)
}

/// wait for the daemon process to shutdown
pub fn wait_until_shutdown(daemon: &Daemon) -> Result<(), Error> {
    for _ in 0..10 {
        thread::sleep(Duration::from_secs(1));
        if !daemon.alive.load(Ordering::Relaxed) {
            return Ok(());
        }
    }
    Err(Error::NotStopped)
}
