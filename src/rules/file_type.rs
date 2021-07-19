use std::fmt::{Display, Formatter};

#[derive(Clone, Debug, PartialEq)]
pub enum FileType {
    Any,
    Macro(MacroDef),
    Mime(MimeType),
}

impl FileType {
    pub fn new_mime_type(name: &str) -> FileType {
        FileType::Mime(MimeType(name.into()))
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct MimeType(pub String);

#[derive(Clone, Debug, PartialEq)]
pub struct MacroDef {
    pub name: String,
    pub mime: Vec<MimeType>,
}

impl MacroDef {
    pub fn new(name: &str, list: Vec<MimeType>) -> Self {
        MacroDef {
            name: name.into(),
            mime: list,
        }
    }
}

impl Display for MimeType {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.0)
    }
}

impl Display for MacroDef {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let list: String = self
            .mime
            .iter()
            .map(|mt| mt.0.clone())
            .collect::<Vec<String>>()
            .join(",");
        f.write_fmt(format_args!("%{}={}", &self.name, list))
    }
}

impl Display for FileType {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.write_str("ftype=")?;
        match self {
            FileType::Any => f.write_str("any"),
            FileType::Macro(md) => f.write_fmt(format_args!("ftype={}", md.name)),
            FileType::Mime(mt) => f.write_fmt(format_args!("ftype={}", mt.0)),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn mime_types_from_list(csv: &str) -> Vec<MimeType> {
        csv.split(',')
            .into_iter()
            .map(|x| MimeType(x.into()))
            .collect()
    }

    #[test]
    fn display() {
        let ft1 = FileType::new_mime_type("text/x-lua");
        assert_eq!(format!("{}", ft1), format!("{}", &ft1));
    }

    #[test]
    fn macro_mime_list() {
        let l = "application/x-bytecode.ocaml,application/x-bytecode.python,application/java-archive,text/x-java";
        let t = MacroDef::new("lang", mime_types_from_list(l));
        assert_eq!(format!("%lang={}", l), format!("{}", t));
    }
}
