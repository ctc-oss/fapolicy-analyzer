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
use std::os::unix::prelude::CommandExt;
use std::path::PathBuf;
use std::process::{Child, Command, Output, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::mpsc::Sender;
use std::sync::{mpsc, Arc};
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
    stdout: Option<String>,
    cb_done: Option<PyObject>,
    cb_exec: Option<PyObject>,
    cb_ping: Option<PyObject>,
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
    fn set_stdout(&mut self, path: &str) {
        self.stdout = Some(path.to_string());
    }

    #[setter]
    fn set_done_callback(&mut self, f: PyObject) {
        self.cb_done = Some(f);
    }

    #[setter]
    fn set_exec_callback(&mut self, f: PyObject) {
        self.cb_exec = Some(f);
    }

    #[setter]
    fn set_ping_callback(&mut self, f: PyObject) {
        self.cb_ping = Some(f);
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
        if let Some(path) = self.stdout.as_ref().map(PathBuf::from) {
            if path.exists() {
                eprintln!(
                    "warning: deleting existing log file from {}",
                    path.display()
                );
                std::fs::remove_file(&path)?;
            }
            rs.stdout_log = Some(path);
        }

        // build the target commands
        let targets: Vec<_> = targets.iter().map(|t| self.build(t)).collect();

        // channel for async communication with py
        let (tx, rx) = mpsc::channel();

        // cloned handles to move into the exec thread
        let cb_exec = self.cb_exec.clone();
        let cb_ping = self.cb_ping.clone();
        let cb_done = self.cb_done.clone();

        // python accessible kill flag from proc handle
        let proc_handle = ProcHandle::default();
        let term = proc_handle.kill_flag.clone();

        // exec thread is responsible for daemon control and target execution
        thread::spawn(move || {
            rs.activate_with_rules(db.as_ref())
                .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
                .expect("activate profiler");

            // todo;; the deactivate call must run even if this fails
            //        perhaps, rather than propogating the errors here,
            //        log the results to a dict that is returned in err
            for (mut cmd, args) in targets {
                if term.load(Ordering::Relaxed) {
                    println!("Profiling terminated");
                    break;
                }

                println!("============= exec `{args}` =================");
                let mut execd = Execd::new(cmd.spawn().unwrap());
                let handle = ExecHandle::new(execd.pid().unwrap(), tx.clone());

                if let Some(cb) = cb_exec.as_ref() {
                    Python::with_gil(|py| {
                        if cb.call1(py, (handle.clone(),)).is_err() {
                            eprintln!("failed make 'exec' callback");
                        }
                    });
                }

                while let Ok(true) = execd.running() {
                    if term.load(Ordering::Relaxed) {
                        execd.kill().expect("kill fail (term)");
                        break;
                    }

                    match rx.try_recv() {
                        Ok(ExecCtrl::Kill) => {
                            execd.kill().expect("kill fail");
                            break;
                        }
                        Ok(ExecCtrl::Abort) => {
                            execd.abort().expect("abort fail");
                            break;
                        }
                        _ => thread::sleep(Duration::from_secs(1)),
                    };

                    if let Some(cb) = cb_ping.as_ref() {
                        Python::with_gil(|py| {
                            if cb.call1(py, (handle.clone(),)).is_err() {
                                eprintln!("failed make 'ping' callback");
                            }
                        });
                    }
                }
            }

            if let Some(cb) = cb_done.as_ref() {
                Python::with_gil(|py| {
                    if cb.call0(py).is_err() {
                        eprintln!("failed make 'done' callback");
                    }
                });
            }

            rs.deactivate()
                .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
                .expect("deactivate profiler");
        });

        Ok(proc_handle)
    }
}

#[derive(Default, Debug, Clone)]
#[pyclass(module = "daemon", name = "ProcHandle")]
struct ProcHandle {
    kill_flag: Arc<AtomicBool>,
}

#[pymethods]
impl ProcHandle {
    fn kill(&self) {
        self.kill_flag.store(true, Ordering::Relaxed);
    }
}

enum ExecCtrl {
    Kill,
    Abort,
}

#[derive(Debug, Clone)]
#[pyclass(module = "daemon", name = "ExecHandle")]
struct ExecHandle {
    pid: u32,
    tx: Sender<ExecCtrl>,
}

impl ExecHandle {
    fn new(pid: u32, tx: Sender<ExecCtrl>) -> Self {
        ExecHandle { pid, tx }
    }
}

#[pymethods]
impl ExecHandle {
    #[getter]
    fn pid(&self) -> u32 {
        self.pid
    }

    fn kill(&self) {
        self.tx.send(ExecCtrl::Kill).unwrap();
    }
}

struct Execd {
    proc: Option<Child>,
    output: Option<Output>,
}

impl Execd {
    fn new(proc: Child) -> Execd {
        Execd {
            proc: Some(proc),
            output: None,
        }
    }

    /// get the process id (pid) if currently active
    fn pid(&self) -> PyResult<u32> {
        match self.proc.as_ref() {
            Some(c) => Ok(c.id()),
            None => Err(PyRuntimeError::new_err("No process")),
        }
    }

    /// check to see if the process is still running
    fn running(&mut self) -> PyResult<bool> {
        match self.proc.as_mut().unwrap().try_wait() {
            Ok(Some(_)) => Ok(false),
            Ok(None) => Ok(true),
            Err(e) => Err(PyRuntimeError::new_err(format!("{:?}", e))),
        }
    }

    /// cancel the process, without blocking, no output will be available
    fn kill(&mut self) -> PyResult<()> {
        println!("killed");
        self.proc
            .as_mut()
            .unwrap()
            .kill()
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))
    }

    /// cancel the process, blocking until it ends, output is available
    fn abort(&mut self) -> PyResult<()> {
        self.kill()?;
        let output = self
            .proc
            .take()
            .unwrap()
            .wait_with_output()
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))?;
        self.output = Some(output);
        Ok(())
    }
}

impl PyProfiler {
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

        // todo;; externalize the output destination for target stderr/stdout
        // println!("{}", String::from_utf8(out.stdout)?);
        // println!("{}", String::from_utf8(out.stderr)?);
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyProfiler>()?;
    m.add_class::<ProcHandle>()?;
    m.add_class::<ExecHandle>()?;
    Ok(())
}
