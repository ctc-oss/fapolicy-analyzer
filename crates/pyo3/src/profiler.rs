/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::{PyResult, Python};
use std::os::unix::prelude::CommandExt;
use std::process::Command;

use fapolicy_daemon::profiler::Profiler;
use fapolicy_rules::read::load_rules_db;

#[pyclass(module = "daemon", name = "Profiler")]
pub struct PyProfiler {
    uid: Option<u32>,
    gid: Option<u32>,
    rules: Option<String>,
}

#[pymethods]
impl PyProfiler {
    #[new]
    fn new() -> Self {
        Self {
            uid: None,
            gid: None,
            rules: None,
        }
    }

    #[setter]
    fn set_uid(&mut self, uid: u32) {
        self.uid = Some(uid);
    }

    #[setter]
    fn set_gid(&mut self, gid: u32) {
        self.gid = Some(gid);
    }

    #[setter]
    fn set_rules(&mut self, path: &str) {
        self.rules = Some(path.to_string())
    }

    fn run(&mut self, args: &str) -> PyResult<()> {
        let opts: Vec<&str> = args.split(" ").collect();
        let target = opts.first().expect("target not specified");
        let args: Vec<&&str> = opts.iter().skip(1).collect();

        let db = self
            .rules
            .as_ref()
            .map(|p| load_rules_db(&p).expect("failed to load rules"));

        let mut rs = Profiler::new();
        rs.activate_with_rules(db.as_ref())
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))?;

        let mut cmd = Command::new(target);
        if let Some(uid) = self.uid {
            cmd.uid(uid);
        }
        if let Some(gid) = self.gid {
            cmd.gid(gid);
        }
        let out = cmd.args(args).output()?;
        println!("{}", String::from_utf8(out.stdout)?);
        rs.deactivate()
            .map_err(|e| PyRuntimeError::new_err(format!("{:?}", e)))?;

        Ok(())
    }
}

pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyProfiler>()?;
    Ok(())
}
