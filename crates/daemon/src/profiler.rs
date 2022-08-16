use crate::error::Error;
use crate::svc::{wait_for_daemon, Handle, State};
use std::fs;
use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use std::process::Command;

const PROFILER_UNIT_NAME: &str = "fapolicyp";
const PROFILER_UNIT: &str = r#"
[Unit]
Description=File Access Profiling Daemon
DefaultDependencies=no
After=local-fs.target systemd-tmpfiles-setup.service

[Service]
#Type=forking
PIDFile=/run/fapolicyp.pid
#ExecStart=/usr/sbin/fapolicyd --debug --permissive --no-details
ExecStart=sleepy

[Install]
WantedBy=multi-user.target
"#;

pub struct Profiler {
    name: String,
    prev: Option<State>,
}

impl Default for Profiler {
    fn default() -> Self {
        Profiler {
            name: PROFILER_UNIT_NAME.to_string(),
            prev: None,
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
        let daemon = Handle::default();
        if !self.is_active()? {
            // 1. preserve daemon state
            self.prev = Some(daemon.state()?);
            // 2. stop daemon if running
            match &self.prev {
                Some(State::Active) => daemon.stop()?,
                _ => {}
            }
            // 3. write the profiler unit file
            write_drop_in()?;
            // 4. start the profiler
            self.handle().start()?;
            // 5. wait for the profiler to become active
            wait_for_daemon(&self.handle(), State::Active, 10)?;
        }
        daemon.state()
    }

    pub fn deactivate(&mut self) -> Result<State, Error> {
        let daemon = Handle::default();
        if self.is_active()? {
            self.handle().stop()?;
            wait_for_daemon(&self.handle(), State::Inactive, 10)?;
            match &self.prev {
                Some(State::Active) => daemon.start()?,
                _ => {}
            }
        }
        self.prev = None;
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
