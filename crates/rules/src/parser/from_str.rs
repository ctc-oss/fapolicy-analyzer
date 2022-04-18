use crate::parser::parse::*;
use crate::parser::{decision, object, permission, subject};
use crate::{Decision, Object, Permission, Subject};
use std::str::FromStr;

impl FromStr for Decision {
    type Err = String;

    fn from_str(i: &str) -> Result<Self, Self::Err> {
        match decision::parse(StrTrace::new(i)) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Decision from string".into()),
        }
    }
}

impl FromStr for Permission {
    type Err = String;

    fn from_str(i: &str) -> Result<Self, Self::Err> {
        match permission::parse(StrTrace::new(i)) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Permission from string".into()),
        }
    }
}

impl FromStr for Subject {
    type Err = String;

    fn from_str(i: &str) -> Result<Self, Self::Err> {
        match subject::parse(StrTrace::new(i)) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Subject from string".into()),
        }
    }
}

impl FromStr for Object {
    type Err = String;

    fn from_str(i: &str) -> Result<Self, Self::Err> {
        match object::parse(StrTrace::new(i)) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Object from string".into()),
        }
    }
}
