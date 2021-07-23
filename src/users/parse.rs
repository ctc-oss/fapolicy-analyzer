use nom::bytes::complete::tag;
use nom::character::complete::{alphanumeric1, digit1};
use nom::combinator::opt;
use nom::sequence::terminated;

use crate::users::User;

/// # An /etc/passwd User parser
/// Simple parser for the passwd format.
/// Reference https://tldp.org/LDP/lame/LAME/linux-admin-made-easy/shadow-file-formats.html
///
/// ## Fields
/// We do not use all of these fields, they are listed here for reference
///
/// ```plain
/// daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
///    1   2 3 4    5       6             7
/// ```
///
/// 1. Username
/// 2. An "x" in the password field
/// 3. Numeric user id
/// 4. Numeric group id
/// 5. Full name of user
/// 6. User's home directory
/// 7. User's shell account
///
pub fn user(i: &str) -> nom::IResult<&str, User> {
    match nom::combinator::complete(nom::sequence::tuple((
        terminated(alphanumeric1, tag(":")),
        terminated(opt(tag("x")), tag(":")),
        terminated(digit1, tag(":")),
        terminated(digit1, tag(":")),
        terminated(any, tag(":")),
        terminated(any, tag(":")),
        any,
    )))(i)
    {
        Ok((remaining_input, (user, _, uid, gid, _, home, shell))) => Ok((
            remaining_input,
            User {
                name: user.into(),
                uid: uid.parse().unwrap(),
                gid: gid.parse().unwrap(),
                home: home.into(),
                shell: shell.into(),
            },
        )),
        Err(e) => Err(e),
    }
}

fn any(i: &str) -> nom::IResult<&str, &str> {
    nom::bytes::complete::is_not(":")(i)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_entry() {
        let (rem, u) = user("daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin")
            .ok()
            .unwrap();

        assert!(rem.is_empty());
        assert_eq!("daemon", &u.name);
        assert_eq!(1, u.uid);
        assert_eq!(1, u.gid);
        assert_eq!("/usr/sbin", &u.home);
        assert_eq!("/usr/sbin/nologin", &u.shell);
    }
}
