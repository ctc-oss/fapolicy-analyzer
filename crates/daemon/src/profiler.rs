/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::time::Duration;
use std::{fs, io, thread};

use tempfile::NamedTempFile;

use fapolicy_rules::db::DB;
use fapolicy_rules::write;

use crate::error::Error;
use crate::fapolicyd::COMPILED_RULES_PATH;
use crate::svc;
use crate::svc::{wait_for_service, State};

const PROFILER_NAME: &str = "fapolicyp";

pub struct Profiler {
    daemon: Daemon,
    prev_state: Option<State>,
    prev_rules: Option<NamedTempFile>,
    pub events_log: Option<PathBuf>,
}

impl Default for Profiler {
    fn default() -> Self {
        Profiler {
            prev_state: None,
            prev_rules: None,
            events_log: None,
            daemon: Daemon::new(PROFILER_NAME),
        }
    }
}

impl Profiler {
    pub fn new() -> Self {
        Default::default()
    }

    pub fn is_active(&self) -> bool {
        self.daemon.active()
    }

    pub fn activate(&mut self) -> Result<State, Error> {
        self.activate_with_rules(None)
    }

    pub fn activate_with_rules(&mut self, db: Option<&DB>) -> Result<State, Error> {
        let fapolicyd = svc::Handle::default();
        if !self.is_active() {
            // 1. preserve daemon state
            self.prev_state = Some(fapolicyd.state()?);
            // 2. stop daemon if running
            if let Some(State::Active) = self.prev_state {
                // todo;; probably need to ensure its not in
                //        a state like restart, init or some such
                fapolicyd.stop()?
            }
            // 3. swap the rules file if necessary
            if let Some(db) = db {
                // compiled.rules is always at the default location
                let compiled = PathBuf::from(COMPILED_RULES_PATH);
                // create a temp file as the backup location
                let backup = NamedTempFile::new()?;
                // move original compiled to backup location
                fs::rename(&compiled, &backup)?;
                // write compiled rules for the profiling run
                write::compiled_rules(db, &compiled)?;
                eprintln!("rules backed up to {:?}", backup.path());
                self.prev_rules = Some(backup);
            }
            // 5. start the profiler
            self.daemon.start(self.events_log.as_ref())?;
            // 6. wait for the profiler to become active
            //wait_for_service(&self.handle(), State::Active, 10)?;
        }
        fapolicyd.state()
    }

    pub fn deactivate(&mut self) -> Result<State, Error> {
        let daemon = svc::Handle::default();
        if self.is_active() {
            // 1. stop the daemon
            self.daemon.stop();
            // 2. wait for the profiler to become inactive
            // wait_for_service(&self.handle(), State::Inactive, 10)?;
            // 3. swap original rules back in if they were changed
            if let Some(f) = self.prev_rules.take() {
                // persist the temp file as the compiled rules
                f.persist(COMPILED_RULES_PATH).map_err(|e| e.error)?;
            }
            // 4. start daemon if it was previously active
            if let Some(State::Active) = self.prev_state {
                eprintln!("restarting daemon");
                daemon.start()?;
            }
        }
        // clear the prev state
        self.prev_state = None;
        // delete the service file
        daemon.state()
    }
}

struct Daemon {
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
        let alive: Arc<AtomicBool> = Default::default();
        let term: Arc<AtomicBool> = Default::default();

        thread::spawn(move || {
            let mut execd = Execd::new(cmd.spawn().unwrap());

            // the process is now alive
            alive.store(true, Ordering::Relaxed);

            while let Ok(true) = execd.running() {
                thread::sleep(Duration::from_secs(1));
                if term.load(Ordering::Relaxed) {
                    execd.kill().expect("kill fail (term)");
                    break;
                }
            }
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
        println!("writing stderr to {}", path.display());
        let mut f = File::create(path).unwrap();
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

    /// Get the process id (pid), None if inactive
    fn pid(&self) -> Option<u32> {
        self.proc.as_ref().map(|p| p.id())
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
