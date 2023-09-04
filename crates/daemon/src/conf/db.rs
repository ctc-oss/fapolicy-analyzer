use crate::conf::config::ConfigToken;
use std::slice::Iter;

#[derive(Clone, Debug)]
pub enum Line {
    Valid(ConfigToken),
    Invalid(String, String),
    Malformed(String),
    Duplicate(ConfigToken),
    Comment(String),
    BlankLine,
}

#[derive(Clone, Debug, Default)]
pub struct DB {
    lines: Vec<Line>,
}

impl DB {
    // see the rules db
    pub fn iter(&self) -> Iter<'_, Line> {
        self.lines.iter()
    }
}

impl From<Vec<Line>> for DB {
    fn from(lines: Vec<Line>) -> Self {
        Self { lines }
    }
}
