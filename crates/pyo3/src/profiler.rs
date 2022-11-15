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
use std::process::Command;

use fapolicy_daemon::profiler::Profiler;
use fapolicy_rules::read::load_rules_db;

type EnvVars = HashMap<String, String>;

#[derive(Default)]
#[pyclass(module = "daemon", name = "Profiler")]
pub struct PyProfiler {
    uid: Option<u32>,
    gid: Option<u32>,
    pwd: Option<PathBuf>,
    env: Option<EnvVars>,
    rules: Option<String>,
    stdout: Option<String>,
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
        self.stdout = Some(path.to_string())
    }

    fn profile(&self, target: &str) -> PyResult<()> {
        self.profile_all(vec![target])
    }

    fn profile_all(&self, targets: Vec<&str>) -> PyResult<()> {
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
            .map(|p| load_rules_db(&p).expect("failed to load rules"));

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

        rs.activate_with_rules(db.as_ref())
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))?;

        // todo;; the deactivate call must run even if this fails
        //        perhaps, rather than propogating the errors here,
        //        log the results to a dict that is returned in err
        for target in targets {
            self.exec(target)?;
        }

        rs.deactivate()
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))?;

        Ok(())
    }
}

impl PyProfiler {
    fn exec(&self, args: &str) -> PyResult<()> {
        let opts: Vec<&str> = args.split(" ").collect();
        let target = opts.first().expect("target not specified");
        let args: Vec<&&str> = opts.iter().skip(1).collect();

        let mut cmd = Command::new(target);
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
        let out = cmd.args(args).output()?;
        println!("{}", String::from_utf8(out.stdout)?);

        Ok(())
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyProfiler>()?;
    Ok(())
}
