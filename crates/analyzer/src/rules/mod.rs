pub use self::decision::Decision;
pub use self::file_type::Rvalue;
pub use self::object::Object;
pub use self::object::Part as ObjPart;
pub use self::permission::Permission;
pub use self::rule::Rule;
pub use self::set::Set;
pub use self::subject::Part as SubjPart;
pub use self::subject::Subject;

mod decision;
mod file_type;
mod object;
pub mod parse;

pub mod db;
mod permission;
pub mod read;
mod rule;
mod set;
mod subject;

pub(crate) fn bool_to_c(b: bool) -> char {
    if b {
        '1'
    } else {
        '0'
    }
}
