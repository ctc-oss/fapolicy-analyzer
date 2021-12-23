/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use std::fmt;
use std::process::Command;
use std::time::Duration;

use dbus::blocking::{BlockingSender, Connection};
use dbus::Message;

use crate::error::Error;
use crate::error::Error::*;
use crate::svc::Method::*;

#[derive(Debug)]
pub enum Method {
    StartUnit,
    StopUnit,
    EnableUnitFiles,
    DisableUnitFiles,
}

impl fmt::Display for Method {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        fmt::Debug::fmt(self, f)
    }
}

fn call(msg: Message) -> Result<Message, Error> {
    Connection::new_system()
        .and_then(|conn| conn.send_with_reply_and_block(msg, Duration::from_millis(2000)))
        .map_err(Error::DbusFailure)
}

fn msg(m: Method, unit: &str) -> Result<Message, Error> {
    dbus::Message::new_method_call(
        "org.freedesktop.systemd1",
        "/org/freedesktop/systemd1",
        "org.freedesktop.systemd1.Manager",
        m.to_string(),
    )
    .map_err(DbusMethodCall)
    .map(|m| m.append2(unit, "fail"))
}

/// a handle to a service that can be signalled by dbus
#[derive(Clone)]
pub struct Handle {
    name: String,
}

impl Default for Handle {
    fn default() -> Self {
        Handle::new("fapolicyd")
    }
}

impl Handle {
    pub fn new(name: &str) -> Handle {
        Handle {
            name: format!("{}.service", name),
        }
    }

    pub fn start(&self) -> Result<(), Error> {
        msg(StartUnit, &self.name).and_then(call).map(|_| ())
    }

    pub fn stop(&self) -> Result<(), Error> {
        msg(StopUnit, &self.name).and_then(call).map(|_| ())
    }

    pub fn enable(&self) -> Result<(), Error> {
        msg(EnableUnitFiles, &self.name).and_then(call).map(|_| ())
    }

    pub fn disable(&self) -> Result<(), Error> {
        msg(DisableUnitFiles, &self.name).and_then(call).map(|_| ())
    }

    // todo;; replace with direct dbus calls
    // systemctl return codes
    // 0 - unit is active
    // 1 - unit not failed
    // 2 - unused
    // 3 - unit is not active
    // 4 - no such unit
    pub fn active(&self) -> Result<bool, Error> {
        Command::new("systemctl")
            .arg("--no-pager")
            .arg("-n0")
            .arg("status")
            .arg(&self.name)
            .output()
            .map(|o| {
                if o.status.success() {
                    Ok(String::from_utf8(o.stdout)?)
                } else {
                    match o.status.code() {
                        Some(1 | 3) => Ok(String::from_utf8(o.stdout)?),
                        Some(4) => Err(ServiceCheckFailure(
                            String::from_utf8(o.stderr)?.trim().into(),
                        )),
                        // unlikely; either got an unused 2-code or a sigint
                        _ => Err(ServiceCheckFailure("Unexpected".into())),
                    }
                }
            })
            .map_err(|_| ServiceCheckFailure("Failed to execute systemctl".into()))?
            .map(|txt| txt.contains("Active: active"))
    }
}
