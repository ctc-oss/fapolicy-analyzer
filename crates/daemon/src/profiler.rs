/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fs;
use std::path::PathBuf;

use tempfile::NamedTempFile;

use fapolicy_rules::db::DB;
use fapolicy_rules::write;

use crate::error::Error;
use crate::error::Error::ProfilerAlreadyActive;
use crate::fapolicyd::{Daemon, COMPILED_RULES_PATH};
use crate::svc::{wait_for_service, State};
use crate::{fapolicyd, svc};

const PROFILER_NAME: &str = "fapolicyp";

pub struct Profiler {
    fapolicyp: Daemon,
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
            fapolicyp: Daemon::new(PROFILER_NAME),
        }
    }
}

impl Profiler {
    pub fn new() -> Self {
        Default::default()
    }

    pub fn is_active(&self) -> bool {
        self.fapolicyp.active()
    }

    pub fn activate(&mut self) -> Result<PathBuf, Error> {
        self.activate_with_rules(None)
    }

    pub fn activate_with_rules(&mut self, db: Option<&DB>) -> Result<PathBuf, Error> {
        let fapolicyd = svc::Handle::default();
        if self.is_active() {
            return Err(ProfilerAlreadyActive);
        }

        // 1. preserve fapolicyd daemon state
        self.prev_state = Some(fapolicyd.state()?);
        // 2. stop fapolicyd daemon if running
        if let Some(State::Active) = self.prev_state {
            // todo;; probably need to ensure its not in
            //        a state like restart, init or some such
            fapolicyd.stop()?;
            wait_for_service(&fapolicyd, State::Inactive, 10)?;
        }
        // 3. swap the rules file if necessary
        if let Some(db) = db {
            // compiled.rules is always at the default location
            let compiled = PathBuf::from(COMPILED_RULES_PATH);
            // create a temp file as the backup location
            let backup = NamedTempFile::new()?;
            // move original compiled to backup location
            fs::rename(&compiled, &backup).or_else(|x| {
                log::debug!("rename fallback copy");
                fs::copy(&compiled, &backup)
                    .and_then(|_| fs::remove_file(&compiled))
                    .or(Err(x))
            })?;
            // write compiled rules for the profiling run
            write::compiled_rules(db, &compiled)?;
            log::debug!("rules backed up to {:?}", backup.path());
            self.prev_rules = Some(backup);
        }
        // 5. resolve the output file
        let outfile = match &self.events_log {
            Some(p) => p.clone(),
            None => NamedTempFile::new()?.into_temp_path().to_path_buf(),
        };
        log::debug!("events-file: {}", outfile.display());

        // 6. start the profiler daemon
        self.fapolicyp.start(Some(&outfile))?;

        // 7. wait for the profiler daemon to become active
        if fapolicyd::wait_until_ready(&outfile).is_err() {
            log::warn!("wait_until_ready failed");
        };

        Ok(outfile)
    }

    pub fn deactivate(&mut self) -> Result<State, Error> {
        let fapolicyd = svc::Handle::default();
        if self.is_active() {
            // 1. stop the profiler daemon
            self.fapolicyp.stop();
            // 2. wait for the profiler daemon to become inactive
            fapolicyd::wait_until_shutdown(&self.fapolicyp)?;
            // 3. swap original rules back in if they were changed
            if let Some(f) = self.prev_rules.take() {
                // persist the temp file as the compiled rules
                f.persist(COMPILED_RULES_PATH).map_err(|e| e.error)?;
            }
            // 4. start fapolicyd daemon if it was previously active
            if let Some(State::Active) = self.prev_state {
                fapolicyd.start()?;
            }
        }
        // clear the prev state
        self.prev_state = None;
        fapolicyd.state()
    }
}
