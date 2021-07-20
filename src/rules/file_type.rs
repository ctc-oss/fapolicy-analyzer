use std::fmt::{Display, Formatter};

#[derive(Clone, Debug, PartialEq)]
pub enum Rvalue {
    Any,
    Literal(String),
    Macro(MacroDef),
}

impl Rvalue {
    pub fn new_mime_type(name: &str) -> Rvalue {
        Rvalue::Literal(name.into())
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct MacroDef {
    pub name: String,
    pub values: Vec<String>,
}

impl MacroDef {
    pub fn new(name: &str, list: Vec<String>) -> Self {
        MacroDef {
            name: name.into(),
            values: list,
        }
    }
}

impl Display for MacroDef {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let list: String = self.values.join(",");
        f.write_fmt(format_args!("%{}={}", &self.name, list))
    }
}

impl Display for Rvalue {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Rvalue::Any => f.write_str("any"),
            Rvalue::Literal(l) => f.write_fmt(format_args!("{}", l)),
            Rvalue::Macro(m) => f.write_fmt(format_args!("{}", m.name)),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn display() {
        let ft1 = Rvalue::new_mime_type("text/x-lua");
        assert_eq!(format!("{}", ft1), format!("{}", &ft1));
    }

    #[test]
    fn macro_mime_list() {
        let l = "application/x-bytecode.ocaml,application/x-bytecode.python,application/java-archive,text/x-java";
        let t = MacroDef::new("lang", l.split(',').map(|s| s.into()).collect());
        assert_eq!(format!("%lang={}", l), format!("{}", t));
    }
}
