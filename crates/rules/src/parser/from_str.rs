use crate::parser::parse::*;
use crate::{Decision, Object, Permission, Subject};
use std::str::FromStr;

impl FromStr for Decision {
    type Err = String;

    fn from_str(i: &str) -> Result<Self, Self::Err> {
        match decision(StrTrace::new(i)) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Decision from string".into()),
        }
    }
}

impl FromStr for Permission {
    type Err = String;

    fn from_str(i: &str) -> Result<Self, Self::Err> {
        match permission(StrTrace::new(i)) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Permission from string".into()),
        }
    }
}

impl FromStr for Subject {
    type Err = String;

    fn from_str(i: &str) -> Result<Self, Self::Err> {
        match subject(StrTrace::new(i)) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Subject from string".into()),
        }
    }
}

impl FromStr for Object {
    type Err = String;

    fn from_str(i: &str) -> Result<Self, Self::Err> {
        match object(StrTrace::new(i)) {
            Ok((_, s)) => Ok(s),
            Err(_) => Err("Failed to parse Object from string".into()),
        }
    }
}
