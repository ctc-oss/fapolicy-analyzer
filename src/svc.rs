use std::fmt;
use std::time::Duration;

use dbus::blocking::{BlockingSender, Connection};
use dbus::{Error, Message};

use crate::svc::Method::{DisableUnitFiles, EnableUnitFiles, StartUnit, StopUnit};

#[derive(Debug)]
enum Method {
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
        .unwrap()
        .send_with_reply_and_block(msg, Duration::from_millis(5000))
}

fn msg(m: Method) -> Message {
    dbus::Message::new_method_call(
        "org.freedesktop.systemd1",
        "/org/freedesktop/systemd1",
        "org.freedesktop.systemd1.Manager",
        m.to_string(),
    )
    .unwrap_or_else(|e| panic!("{}", e))
}

#[derive(Clone)]
pub struct Daemon {
    name: String,
}

impl Daemon {
    pub fn new(name: &str) -> Daemon {
        Daemon {
            name: name.to_string(),
        }
    }

    pub fn start(&self) -> Result<(), String> {
        let m = msg(StartUnit).append2(self.name.as_str(), "fail");
        match call(m) {
            Ok(_) => Ok(()),
            Err(e) => Err(e.to_string()),
        }
    }
    pub fn stop(&self) -> Result<(), String> {
        let m = msg(StopUnit).append2(self.name.as_str(), "fail");
        match call(m) {
            Ok(_) => Ok(()),
            Err(e) => Err(e.to_string()),
        }
    }
    pub fn enable(&self) -> Result<(), String> {
        let m = msg(EnableUnitFiles).append3(vec![self.name.as_str()], true, false);
        match call(m) {
            Ok(_) => Ok(()),
            Err(e) => Err(e.to_string()),
        }
    }
    pub fn disable(&self) -> Result<(), String> {
        let m = msg(DisableUnitFiles).append2(vec![self.name.as_str()], true);
        match call(m) {
            Ok(_) => Ok(()),
            Err(e) => Err(e.to_string()),
        }
    }
}
