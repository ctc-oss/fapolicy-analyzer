use std::fmt::{Display, Formatter};

#[derive(Clone, Debug, PartialEq)]
pub struct Set {
    pub name: String,
    pub values: Vec<String>,
}

impl Set {
    pub fn new(name: &str, list: Vec<String>) -> Self {
        Set {
            name: name.into(),
            values: list,
        }
    }
}

impl Display for Set {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let list: String = self.values.join(",");
        f.write_fmt(format_args!("%{}={}", &self.name, list))
    }
}
