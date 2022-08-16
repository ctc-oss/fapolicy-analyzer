/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fs;
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;

use tempfile::NamedTempFile;

use fapolicy_rules::db::DB;
use fapolicy_rules::write;

use crate::error::Error;
use crate::fapolicyd::COMPILED_RULES_PATH;
use crate::svc::{wait_for_daemon, Handle, State};

const PROFILER_UNIT_NAME: &str = "fapolicyp";
const PROFILER_UNIT: &str = r#"
[Unit]
Description=File Access Profiling Daemon
DefaultDependencies=no
After=local-fs.target systemd-tmpfiles-setup.service

[Service]
Type=simple
PIDFile=/run/fapolicyp.pid
ExecStart=/usr/sbin/fapolicyd --debug --permissive --no-details
StandardOutput=file:/tmp/fapolicyp.stdout.log
StandardError=file:/tmp/fapolicyp.stderr.log

[Install]
WantedBy=multi-user.target
"#;

pub struct Profiler {
    pub name: String,
    prev_state: Option<State>,
    prev_rules: Option<NamedTempFile>,
}

impl Default for Profiler {
    fn default() -> Self {
        Profiler {
            name: PROFILER_UNIT_NAME.to_string(),
            prev_state: None,
            prev_rules: None,
        }
    }
}

impl Profiler {
    pub fn new() -> Self {
        Default::default()
    }

    fn handle(&self) -> Handle {
        Handle::new(&self.name)
    }

    pub fn is_active(&self) -> Result<bool, Error> {
        self.handle().active()
    }

    pub fn activate(&mut self) -> Result<State, Error> {
        self.activate_with_rules(None)
    }

    pub fn activate_with_rules(&mut self, db: Option<&DB>) -> Result<State, Error> {
        let daemon = Handle::default();
        if !self.is_active()? {
            // 1. preserve daemon state
            self.prev_state = Some(daemon.state()?);
            // 2. stop daemon if running
            if let Some(State::Active) = self.prev_state {
                // todo;; probably need to ensure its not in
                //        a state like restart, init or some such
                daemon.stop()?
            }
            // 3. swap the rules file if necessary
            if let Some(db) = db {
                let compiled = PathBuf::from(COMPILED_RULES_PATH);
                let backup = NamedTempFile::new()?;
                fs::rename(&compiled, &backup)?;
                write::compiled_rules(db, &compiled)?;
                eprintln!("rules backed up to {:?}", backup.path());
                self.prev_rules = Some(backup);
            }
            // 4. write the profiler unit file
            write_drop_in()?;
            // 5. start the profiler
            self.handle().start()?;
            // 6. wait for the profiler to become active
            wait_for_daemon(&self.handle(), State::Active, 10)?;
        }
        daemon.state()
    }

    pub fn deactivate(&mut self) -> Result<State, Error> {
        let daemon = Handle::default();
        if self.is_active()? {
            // 1. stop the daemon
            self.handle().stop()?;
            // 2. wait for the profiler to become inactive
            wait_for_daemon(&self.handle(), State::Inactive, 10)?;
            // 3. swap in alternative rules if specified
            if let Some(f) = self.prev_rules.take() {
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
        delete_drop_in()?;
        daemon.state()
    }

    pub fn rollback(&mut self) -> Result<State, Error> {
        self.deactivate()
    }
}

fn path_to_drop_in() -> String {
    format!("/usr/lib/systemd/system/{}.service", PROFILER_UNIT_NAME)
}

fn write_drop_in() -> Result<(), Error> {
    let mut unit_file = File::create(path_to_drop_in())?;
    unit_file.write_all(PROFILER_UNIT.as_bytes())?;
    Ok(())
}

fn delete_drop_in() -> Result<(), Error> {
    fs::remove_file(PathBuf::from(path_to_drop_in()))?;
    Ok(())
}
