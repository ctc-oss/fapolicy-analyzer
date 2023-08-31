/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use dbus::arg::messageitem::MessageItem;
use std::fmt;
use std::thread::sleep;
use std::time::Duration;

use dbus::blocking::{BlockingSender, Connection};
use dbus::Message;

use crate::error::Error;
use crate::error::Error::*;
use crate::svc::Method::*;

#[derive(Debug)]
pub enum Method {
    Reload,
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

fn method_call(m: Method) -> Result<Message, Error> {
    Message::new_method_call(
        "org.freedesktop.systemd1",
        "/org/freedesktop/systemd1",
        "org.freedesktop.systemd1.Manager",
        m.to_string(),
    )
    .map_err(DbusMethodCall)
}

fn call(msg: Message) -> Result<Message, Error> {
    Connection::new_system()
        .and_then(|conn| conn.send_with_reply_and_block(msg, Duration::from_millis(2000)))
        .map_err(Error::DbusFailure)
}

fn msg(m: Method, unit: &str) -> Result<Message, Error> {
    method_call(m).map(|m| m.append2(unit, "fail"))
}

/// reload all systemd units, ie. systemctl daemon-reload
pub fn daemon_reload() -> Result<(), Error> {
    method_call(Reload).and_then(call).map(|_| ())
}

/// a handle to a service that can be signalled by dbus
#[derive(Clone)]
pub struct Handle {
    pub name: String,
    unit: String,
}

impl Default for Handle {
    fn default() -> Self {
        Handle::new("fapolicyd")
    }
}

#[derive(Clone, Debug, PartialEq)]
pub enum State {
    Active,
    Inactive,
    Failed,
    Other(String),
}

impl State {
    pub fn can_be(&self, other: State) -> bool {
        use State::*;

        match self {
            Inactive if other == Failed => true,
            _ => *self == other,
        }
    }
}

impl Handle {
    pub fn new(name: &str) -> Handle {
        Handle {
            name: name.to_string(),
            unit: format!("{}.service", name),
        }
    }

    pub fn start(&self) -> Result<(), Error> {
        msg(StartUnit, &self.unit).and_then(call).map(|_| ())
    }

    pub fn stop(&self) -> Result<(), Error> {
        msg(StopUnit, &self.unit).and_then(call).map(|_| ())
    }

    pub fn enable(&self) -> Result<(), Error> {
        msg(EnableUnitFiles, &self.unit).and_then(call).map(|_| ())
    }

    pub fn disable(&self) -> Result<(), Error> {
        msg(DisableUnitFiles, &self.unit).and_then(call).map(|_| ())
    }

    pub fn reload(&self) -> Result<(), Error> {
        msg(Reload, &self.unit).and_then(call).map(|_| ())
    }

    pub fn active(&self) -> Result<bool, Error> {
        self.state().map(|state| matches!(state, State::Active))
    }

    pub fn state(&self) -> Result<State, Error> {
        use dbus::arg::messageitem::Props;
        use dbus::ffidisp::Connection;
        use State::*;

        let c = Connection::new_system()?;
        let p = Props::new(
            &c,
            "org.freedesktop.systemd1",
            // todo;; the path name may need to be fetched dynamically via a Message
            format!("/org/freedesktop/systemd1/unit/{}_2eservice", self.name),
            "org.freedesktop.systemd1.Unit",
            5000,
        );

        if let MessageItem::Str(state) = p.get("ActiveState")? {
            Ok(match state.as_str() {
                "active" => Active,
                "inactive" => Inactive,
                "failed" => Failed,
                _ => Other(state),
            })
        } else {
            Err(ServiceCheckFailure(
                "DBUS unit active check failed".to_string(),
            ))
        }
    }

    pub fn valid(&self) -> Result<bool, Error> {
        use dbus::arg::messageitem::Props;
        use dbus::ffidisp::Connection;

        let c = Connection::new_system()?;
        let p = Props::new(
            &c,
            "org.freedesktop.systemd1",
            // todo;; the path name may need to be fetched dynamically via a Message
            format!("/org/freedesktop/systemd1/unit/{}_2eservice", self.name),
            "org.freedesktop.systemd1.Unit",
            5000,
        );

        if let MessageItem::Str(state) = p.get("LoadState")? {
            Ok(matches!(state.as_str(), "loaded"))
        } else {
            Err(ServiceCheckFailure(
                "DBUS unit valid check failed".to_string(),
            ))
        }
    }
}

pub fn wait_for_service(handle: &Handle, target_state: State, seconds: usize) -> Result<(), Error> {
    for _ in 0..seconds {
        log::debug!("waiting on {} to be {target_state:?}...", handle.name);
        sleep(Duration::from_secs(1));
        if handle
            .state()
            .map(|state| target_state.can_be(state))
            .unwrap_or(false)
        {
            log::debug!("{} is now {target_state:?}", handle.name);
            return Ok(());
        }
    }

    let actual_state = handle.state()?;
    log::debug!("done waiting, {} is {target_state:?}", handle.name);

    if target_state.can_be(actual_state) {
        Ok(())
    } else {
        Err(Unresponsive)
    }
}

#[cfg(test)]
mod tests {
    use crate::svc::State::*;

    #[test]
    fn state_can_be() {
        // Failed is Inactive
        assert!(Inactive.can_be(Failed));
        // Inactive is not Failed
        assert!(!Failed.can_be(Inactive));
        // Identity
        assert!(Active.can_be(Active))
    }
}
