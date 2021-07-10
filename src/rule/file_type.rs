use std::fmt::{Display, Formatter};

pub struct FileType(pub String);

impl Display for FileType {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.write_fmt(format_args!("ftype={}", &self.0))
    }
}
