// export
pub use auparse_sys::cursor::*;
pub use auparse_sys::error::Error;
pub use auparse_sys::event::*;
pub use auparse_sys::source::*;

pub type Filter = fn(u32) -> bool;
pub trait Parser<T> {
    type Error;

    fn parse(&self, e: Event) -> Result<T, Self::Error>;
}
