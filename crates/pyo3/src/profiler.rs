/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use fapolicy_analyzer::users::read_users;
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
use std::thread;
use std::time::Duration;

use fapolicy_daemon::profiler::Profiler;
use fapolicy_rules::read::load_rules_db;

type EnvVars = HashMap<String, String>;
type CmdArgs = (Command, String);

#[derive(Default)]
#[pyclass(module = "daemon", name = "Profiler")]
pub struct PyProfiler {
    uid: Option<u32>,
    gid: Option<u32>,
    pwd: Option<PathBuf>,
    env: Option<EnvVars>,
    rules: Option<String>,
    daemon_stdout: Option<String>,
    target_stdout: Option<String>,
    target_stderr: Option<String>,
    callback_done: Option<PyObject>,
    callback_exec: Option<PyObject>,
}

#[pymethods]
impl PyProfiler {
    #[new]
    fn new() -> Self {
        Default::default()
    }

    #[setter]
    fn set_uid(&mut self, uid: u32) {
        self.uid = Some(uid);
    }

    fn set_user(&mut self, uid_or_uname: &str) -> PyResult<()> {
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
        Ok(())
    }

    #[setter]
    fn set_gid(&mut self, gid: u32) {
        self.gid = Some(gid);
    }

    #[setter]
    fn set_pwd(&mut self, path: &str) {
        self.pwd = Some(PathBuf::from(path))
    }

    #[setter]
    fn set_rules(&mut self, path: &str) {
        self.rules = Some(path.to_string())
    }

    #[setter]
    fn set_env(&mut self, args: EnvVars) {
        self.env = Some(args);
    }

    #[setter]
    fn set_daemon_stdout(&mut self, path: &str) {
        self.daemon_stdout = Some(path.to_string());
    }

    #[getter]
    fn get_target_stdout(&self) -> Option<&String> {
        self.target_stdout.as_ref()
    }

    #[setter]
    fn set_target_stdout(&mut self, path: &str) {
        self.target_stdout = Some(path.to_string());
    }

    #[setter]
    fn set_target_stderr(&mut self, path: &str) {
        self.target_stderr = Some(path.to_string());
    }

    #[setter]
    fn set_done_callback(&mut self, f: PyObject) {
        self.callback_done = Some(f);
    }

    #[setter]
    fn set_exec_callback(&mut self, f: PyObject) {
        self.callback_exec = Some(f);
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

        // configure the daemon and target logging outputs
        rs.stdout_log = check_log_dest(self.daemon_stdout.as_ref());
        let stdout_log = create_log_dest(self.target_stdout.as_ref());
        let stderr_log = create_log_dest(self.target_stderr.as_ref());

        // build the target commands
        let targets: Vec<_> = targets.iter().map(|t| self.build(t)).collect();

        // cloned handles to move into the exec thread
        let cb_exec = self.callback_exec.clone();
        let cb_done = self.callback_done.clone();

        // python accessible kill flag from proc handle
        let proc_handle = ProcHandle::default();
        let term = proc_handle.kill_flag.clone();
        let alive = proc_handle.alive_flag.clone();

        // outer thread is responsible for daemon control
        thread::spawn(move || {
            rs.activate_with_rules(db.as_ref())
                .expect("activate profiler");

            // inner thread is responsible for target execution
            let inner = thread::spawn(move || {
                for (mut cmd, args) in targets {
                    if term.load(Ordering::Relaxed) {
                        break;
                    }

                    // start the process, wrapping in the execd helper
                    let mut execd = Execd::new(cmd.spawn().unwrap());

                    // the process is now alive
                    alive.store(true, Ordering::Relaxed);

                    let pid = execd.pid().expect("pid");
                    let handle = ExecHandle::new(pid, args, term.clone());

                    if let Some(cb) = cb_exec.as_ref() {
                        Python::with_gil(|py| {
                            if cb.call1(py, (handle.clone(),)).is_err() {
                                eprintln!("failed make 'exec' callback");
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
                    if let Some(mut f) = stdout_log.as_ref() {
                        f.write_all(&output.stdout).unwrap();
                    }
                    if let Some(mut f) = stderr_log.as_ref() {
                        f.write_all(&output.stderr).unwrap();
                    }
                }
            });

            if let Some(e) = inner.join().err() {
                eprintln!("exec thread panic {:?}", e);
            }

            rs.deactivate().expect("deactivate profiler");

            // callback when all targets are completed / cancelled / failed
            // callback failure here is considered fatal due to the
            // transactional completion nature of this call
            if let Some(cb) = cb_done.as_ref() {
                Python::with_gil(|py| cb.call0(py).expect("done callback failed"));
            }
        });

        Ok(proc_handle)
    }
}

fn check_log_dest(path: Option<&String>) -> Option<PathBuf> {
    let path = path.as_ref().map(PathBuf::from);
    if let Some(path) = path.as_ref() {
        if path.exists() {
            eprintln!(
                "warning: deleting existing log file from {}",
                path.display()
            );
            if std::fs::remove_file(&path).is_err() {
                eprintln!(
                    "warning: failed to delete existing log file from {}",
                    path.display()
                )
            };
        }
    }
    path
}

fn create_log_dest(path: Option<&String>) -> Option<File> {
    if let Some(path) = check_log_dest(path) {
        match File::create(path) {
            Ok(f) => Some(f),
            Err(_) => None,
        }
    } else {
        None
    }
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
}

impl ExecHandle {
    fn new(pid: u32, command: String, kill_flag: Arc<AtomicBool>) -> Self {
        ExecHandle {
            pid,
            command,
            kill_flag,
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
        println!("killed");
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
