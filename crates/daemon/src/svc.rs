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
            name: name.to_string(),
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

    pub fn active(&self) -> Result<bool, Error> {
        Command::new("systemctl")
            .arg("status")
            .arg(&self.name)
            .arg("--no-pager")
            .arg("-n0")
            .output()
            .map(|o| {
                String::from_utf8(o.stdout).map_err(|_| {
                    ServiceStatusQueryFailure("Failed to parse systemctl output".into())
                })
            })
            .map_err(|_| ServiceStatusQueryFailure("Failed to execute systemctl".into()))?
            .map(|txt| txt.contains("Active: active"))
    }
}
