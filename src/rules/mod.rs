mod decision;
pub use self::decision::Decision;

mod file_type;
pub use self::file_type::Rvalue;

mod object;
pub use self::object::Object;

pub mod parse;

mod permission;
pub use self::permission::Permission;

mod rule;
pub use self::rule::Rule;

mod subject;
pub use self::subject::Subject;

mod set;
pub use self::set::Set;

pub(crate) fn bool_to_c(b: bool) -> char {
    if b {
        '1'
    } else {
        '0'
    }
}
