/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use chrono::Utc;
use fapolicy_analyzer::users::read_users;
use fapolicy_daemon::fapolicyd::wait_until_ready;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::{PyResult, Python};
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;
use std::os::unix::prelude::CommandExt;
use std::path::PathBuf;
use std::process::{Child, Command, Output, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::time::{Duration, SystemTime};
use std::{io, thread};

use fapolicy_daemon::profiler::Profiler;
use fapolicy_rules::read::load_rules_db;

type EnvVars = HashMap<String, String>;
type CmdArgs = (Command, String);

#[derive(Debug, Default)]
#[pyclass(module = "daemon", name = "Profiler")]
pub struct PyProfiler {
    uid: Option<u32>,
    gid: Option<u32>,
    pwd: Option<PathBuf>,
    env: Option<EnvVars>,
    rules: Option<String>,
    log_dir: Option<String>,
    callback_exec: Option<PyObject>,
    callback_tick: Option<PyObject>,
    callback_done: Option<PyObject>,
}

#[pymethods]
impl PyProfiler {
    #[new]
    fn new() -> Self {
        Self {
            log_dir: Some("/var/tmp".to_string()),
            ..Default::default()
        }
    }

    #[setter]
    fn set_uid(&mut self, uid: Option<u32>) {
        self.uid = uid;
    }

    #[setter]
    fn set_user(&mut self, uid_or_uname: Option<&str>) -> PyResult<()> {
        if let Some(uid_or_uname) = uid_or_uname {
            self.uid = if uid_or_uname.starts_with(|x: char| x.is_ascii_alphabetic()) {
                Some(
                    read_users()
                        .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))?
                        .iter()
                        .find(|x| x.name == uid_or_uname)
                        .map(|u| u.uid)
                        .ok_or_else(|| {
                            PyRuntimeError::new_err(format!(
                                "unable to lookup uid by uname {}",
                                uid_or_uname
                            ))
                        })?,
                )
            } else {
                Some(uid_or_uname.parse()?)
            };
        }
        Ok(())
    }

    #[setter]
    fn set_gid(&mut self, gid: Option<u32>) {
        self.gid = gid;
    }

    #[setter]
    fn set_pwd(&mut self, path: Option<&str>) {
        self.pwd = path.map(PathBuf::from)
    }

    #[setter]
    fn set_rules(&mut self, path: Option<&str>) {
        self.rules = path.map(String::from)
    }

    /// Accept a dict of String:String KV pairs to set as environment variables
    #[setter]
    fn set_env(&mut self, dict: Option<EnvVars>) {
        self.env = dict;
    }

    #[setter]
    fn set_log_dir(&mut self, path: Option<&str>) {
        self.log_dir = path.map(String::from);
    }

    #[setter]
    fn set_exec_callback(&mut self, f: PyObject) {
        self.callback_exec = Some(f);
    }

    #[setter]
    fn set_tick_callback(&mut self, f: PyObject) {
        self.callback_tick = Some(f);
    }

    #[setter]
    fn set_done_callback(&mut self, f: PyObject) {
        self.callback_done = Some(f);
    }

    fn profile(&self, target: &str) -> PyResult<ProcHandle> {
        self.profile_all(vec![target])
    }

    // accept callback for exec control (eg kill), and done notification
    fn profile_all(&self, targets: Vec<&str>) -> PyResult<ProcHandle> {
        // the working dir must exist prior to execution
        if let Some(pwd) = self.pwd.as_ref() {
            // todo;; stable in 1.63
            // pwd.try_exists()?;
            if !pwd.exists() {
                return Err(PyRuntimeError::new_err(format!(
                    "pwd does not exist {}",
                    pwd.display()
                )));
            }
        }

        let db = self
            .rules
            .as_ref()
            .map(|p| load_rules_db(p).expect("failed to load rules"));

        let mut rs = Profiler::new();

        // generate the daemon and target logs
        let (events_log, mut stdout_log, mut stderr_log) = create_log_files(self.log_dir.as_ref())
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))?;

        // set the daemon stdout log, aka the events log
        if let Some((_, path)) = events_log.as_ref() {
            rs.events_log = Some(path.clone());
        }

        // build the target commands
        let targets: Vec<_> = targets.iter().map(|t| self.build(t)).collect();

        // cloned handles to move into the exec thread
        let cb_exec = self.callback_exec.clone();
        let cb_tick = self.callback_tick.clone();
        let cb_done = self.callback_done.clone();

        // python accessible kill flag from proc handle
        let proc_handle = ProcHandle::default();
        let term = proc_handle.kill_flag.clone();
        let alive = proc_handle.alive_flag.clone();

        // outer thread is responsible for daemon control
        thread::spawn(move || {
            // start the daemon and wait until it is ready
            let start_profiling_daemon = rs
                .activate_with_rules(db.as_ref())
                .and_then(|_| wait_until_ready(&events_log.as_ref().unwrap().1))
                .map_err(|e| e.to_string());

            // if profiling daemon is not ready do not spawn target threads
            let profiling_res = if start_profiling_daemon.is_ok() {
                // inner thread is responsible for target execution
                let target_thread = thread::spawn(move || {
                    for (mut cmd, args) in targets {
                        if term.load(Ordering::Relaxed) {
                            break;
                        }

                        // start the process, wrapping in the execd helper
                        let mut execd = Execd::new(cmd.spawn().unwrap());

                        // the process is now alive
                        alive.store(true, Ordering::Relaxed);

                        let pid = execd.pid().expect("pid");
                        let handle = ExecHandle::new(
                            pid,
                            args,
                            term.clone(),
                            // todo;; clean this up...
                            events_log.as_ref().map(|x| x.1.display().to_string()),
                            stdout_log.as_ref().map(|x| x.1.display().to_string()),
                            stderr_log.as_ref().map(|x| x.1.display().to_string()),
                        );
                        let start = SystemTime::now();

                        if let Some(cb) = cb_exec.as_ref() {
                            Python::with_gil(|py| {
                                if cb.call1(py, (handle.clone(),)).is_err() {
                                    eprintln!("'exec' callback failed");
                                }
                            });
                        }

                        // loop on target completion status, providing opportunity to interrupt
                        while let Ok(true) = execd.running() {
                            thread::sleep(Duration::from_secs(1));
                            if term.load(Ordering::Relaxed) {
                                execd.kill().expect("kill fail (term)");
                                break;
                            }
                            if let Some(cb) = cb_tick.as_ref() {
                                let t = SystemTime::now()
                                    .duration_since(start)
                                    .expect("system time")
                                    .as_secs();
                                Python::with_gil(|py| {
                                    if cb.call1(py, (handle.clone(), t)).is_err() {
                                        eprintln!("'tick' callback failed");
                                    }
                                });
                            }
                        }

                        // we need to wait on the process to die, instead of just blocking
                        // this loop provides the ability to add a harder stop impl, abort
                        term.store(false, Ordering::Relaxed);
                        while let Ok(true) = execd.running() {
                            if term.load(Ordering::Relaxed) {
                                execd.abort().expect("abort fail (term)");
                                break;
                            }
                            thread::sleep(Duration::from_secs(1));
                        }

                        // no longer alive
                        alive.store(false, Ordering::Relaxed);

                        // write the target stdout/stderr if configured
                        let output: Output = execd.into();
                        if let Some((ref mut f, _)) = stdout_log {
                            f.write_all(&output.stdout).unwrap();
                        }
                        if let Some((ref mut f, _)) = stderr_log {
                            f.write_all(&output.stderr).unwrap();
                        }
                    }
                });

                // outer thread waits on the target thread to complete
                target_thread.join().map_err(|e| format!("{:?}", e))
            } else {
                start_profiling_daemon
            };

            // attempt to deactivate if active
            if rs.is_active() {
                if rs.deactivate().is_err() {
                    eprintln!("profiler deactivate failed");
                }
            }

            // done; all targets are completed / cancelled / failed
            if let Some(cb) = cb_done.as_ref() {
                if Python::with_gil(|py| cb.call0(py)).is_err() {
                    eprintln!("'done' callback failed");
                }
            }

            profiling_res.expect("profiling failure");
        });

        Ok(proc_handle)
    }
}

type LogPath = Option<(File, PathBuf)>;
type LogPaths = (LogPath, LogPath, LogPath);
fn create_log_files(log_dir: Option<&String>) -> Result<LogPaths, io::Error> {
    if let Some(log_dir) = log_dir {
        let t = Utc::now().timestamp();

        let event_log = make_log_path(log_dir, t, "events")?;
        let target_stdout = make_log_path(log_dir, t, "stdout")?;
        let target_stderr = make_log_path(log_dir, t, "stderr")?;
        return Ok((event_log, target_stdout, target_stderr));
    }
    Ok((None, None, None))
}

fn make_log_path(log_dir: &str, t: i64, suffix: &str) -> Result<LogPath, io::Error> {
    let path = PathBuf::from(format!("{log_dir}/.fapa{t}.{suffix}"));
    let file = File::create(&path)?;
    Ok(Some((file, path)))
}

/// Terminable process handle returned to python after starting profiling
#[derive(Default, Debug, Clone)]
#[pyclass(module = "daemon", name = "ProcHandle")]
struct ProcHandle {
    kill_flag: Arc<AtomicBool>,
    alive_flag: Arc<AtomicBool>,
}

#[pymethods]
impl ProcHandle {
    #[getter]
    fn running(&self) -> bool {
        self.alive_flag.load(Ordering::Relaxed)
    }

    fn kill(&self) {
        self.kill_flag.store(true, Ordering::Relaxed);
    }
}

#[derive(Debug, Clone)]
#[pyclass(module = "daemon", name = "ExecHandle")]
struct ExecHandle {
    pid: u32,
    command: String,
    kill_flag: Arc<AtomicBool>,
    daemon_stdout_log: Option<String>,
    target_stdout_log: Option<String>,
    target_stderr_log: Option<String>,
}

impl ExecHandle {
    fn new(
        pid: u32,
        command: String,
        kill_flag: Arc<AtomicBool>,
        events_log: Option<String>,
        target_out: Option<String>,
        target_err: Option<String>,
    ) -> Self {
        ExecHandle {
            pid,
            command,
            kill_flag,
            daemon_stdout_log: events_log,
            target_stdout_log: target_out,
            target_stderr_log: target_err,
        }
    }
}

#[pymethods]
impl ExecHandle {
    #[getter]
    fn pid(&self) -> u32 {
        self.pid
    }

    #[getter]
    fn cmd(&self) -> &str {
        &self.command
    }

    #[getter]
    fn event_log(&self) -> Option<String> {
        self.daemon_stdout_log.clone()
    }

    #[getter]
    fn stdout_log(&self) -> Option<String> {
        self.target_stdout_log.clone()
    }

    #[getter]
    fn stderr_log(&self) -> Option<String> {
        self.target_stderr_log.clone()
    }

    fn kill(&self) {
        self.kill_flag.store(true, Ordering::Relaxed);
    }
}

/// Internal struct used to inspect a running process
struct Execd {
    proc: Option<Child>,
}

/// Consume the [Execd] into an [Output], blocking until the process completes
impl From<Execd> for Output {
    fn from(mut value: Execd) -> Self {
        value
            .proc
            .take()
            .unwrap()
            .wait_with_output()
            .expect("failed to get output")
    }
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
    fn running(&mut self) -> PyResult<bool> {
        match self.proc.as_mut().unwrap().try_wait() {
            Ok(Some(_)) => Ok(false),
            Ok(None) => Ok(true),
            Err(e) => Err(PyRuntimeError::new_err(format!("{:?}", e))),
        }
    }

    /// Cancel the process, without blocking
    fn kill(&mut self) -> PyResult<()> {
        self.proc
            .as_mut()
            .unwrap()
            .kill()
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
    }

    /// Kill more
    fn abort(&mut self) -> PyResult<()> {
        eprintln!("abort is not yet implemented");
        Ok(())
    }
}

impl PyProfiler {
    /// Creates a [Command] and configures it according to the [PyProfiler]
    /// Returns a tuple [CmdArgs] type to preserve the target command string
    fn build(&self, args: &str) -> CmdArgs {
        let opts: Vec<&str> = args.split(' ').collect();
        let (target, opts) = opts.split_first().expect("invalid cmd string");

        let mut cmd = Command::new(target);
        cmd.stdout(Stdio::piped());
        cmd.stderr(Stdio::piped());

        if let Some(uid) = self.uid {
            cmd.uid(uid);
        }
        if let Some(gid) = self.gid {
            cmd.gid(gid);
        }
        if let Some(pwd) = self.pwd.as_ref() {
            cmd.current_dir(pwd);
        }
        if let Some(envs) = self.env.as_ref() {
            cmd.envs(envs);
        }

        cmd.args(opts);
        (cmd, args.to_string())
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyProfiler>()?;
    m.add_class::<ProcHandle>()?;
    m.add_class::<ExecHandle>()?;
    Ok(())
}
