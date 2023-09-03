use crate::conf::config::ConfigToken;
use std::slice::Iter;

#[derive(Clone, Debug)]
pub enum Line {
    Valid(ConfigToken),
    Invalid(String),
    Duplicate(ConfigToken),
    Comment(String),
    BlankLine,
}

#[derive(Clone, Debug)]
pub struct File {
    lines: Vec<Line>,
}

impl File {
    // see the rules db
    pub fn iter(&self) -> Iter<'_, Line> {
        self.lines.iter()
    }
}

impl From<Vec<Line>> for File {
    fn from(lines: Vec<Line>) -> Self {
        Self { lines }
    }
}

impl Default for File {
    fn default() -> Self {
        File { lines: vec![] }
    }
}
