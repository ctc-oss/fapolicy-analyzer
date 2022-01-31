/*
 * Copyright Concurrent Technologies Corporation 2021
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

use nom::bytes::complete::{tag, take_while};
use nom::character::complete::digit1;
use nom::combinator::opt;
use nom::multi::separated_list0;
use nom::sequence::terminated;

use crate::users::{Group, User};

/// # An /etc/passwd User parser
/// Simple parser for the passwd file format.
/// Reference https://man7.org/linux/man-pages/man5/passwd.5.html
///
/// ## Fields
/// We do not use all of these fields, they are listed here for reference
///
/// Each line of the file describes a single user and contains seven colon-separated fields:
/// ```plain
/// daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
///    1   2 3 4    5       6             7
/// ```
///
/// 1. Username
/// 2. Password (either the encrypted user password, an asterisk (*), or the letter 'x')
/// 3. Numeric user id
/// 4. Numeric group id
/// 5. Full name of user
/// 6. User's home directory
/// 7. User's shell account
///
pub fn user(i: &str) -> nom::IResult<&str, User> {
    match nom::combinator::complete(nom::sequence::tuple((
        terminated(valid_name, tag(":")),
        terminated(opt(tag("x")), tag(":")),
        terminated(digit1, tag(":")),
        terminated(digit1, tag(":")),
        terminated(opt(any), tag(":")),
        terminated(any, tag(":")),
        filepath,
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

/// # An /etc/group Group parser
/// Simple parser for the group file format.
/// Reference https://man7.org/linux/man-pages/man5/group.5.html
///
/// ## Fields
/// We do not use all of these fields, they are listed here for reference
///
/// Each line of the file describes a single group and contains four colon-separated fields:
/// ```plain
/// group_name:password:GID:user_list
/// ```
/// 1. Groupname
/// 2. Password, either the encrypted user password, an asterisk (*), or the letter 'x'
/// 3. Numeric group id
/// 4. User list, separated by commas
///
pub fn group(i: &str) -> nom::IResult<&str, Group> {
    match nom::combinator::complete(nom::sequence::tuple((
        terminated(valid_name, tag(":")),
        terminated(opt(tag("x")), tag(":")),
        terminated(digit1, tag(":")),
        separated_list0(tag(","), valid_name),
    )))(i)
    {
        Ok((remaining_input, (user, _, gid, list))) => Ok((
            remaining_input,
            Group {
                name: user.into(),
                gid: gid.parse().unwrap(),
                users: list
                    .iter()
                    .filter(|s| !s.is_empty())
                    .map(|s| s.to_string())
                    .collect(),
            },
        )),
        Err(e) => Err(e),
    }
}

fn any(i: &str) -> nom::IResult<&str, &str> {
    nom::bytes::complete::is_not(":")(i)
}

fn valid_name(i: &str) -> nom::IResult<&str, &str> {
    take_while(|x| nom::character::is_alphanumeric(x as u8) || x == '-' || x == '_')(i)
}

fn filepath(i: &str) -> nom::IResult<&str, &str> {
    nom::bytes::complete::is_not(" \t\n")(i)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_passwd_entry() {
        let (rem, u) = user("daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin")
            .ok()
            .unwrap();

        assert!(rem.is_empty());
        assert_eq!("daemon", &u.name);
        assert_eq!(1, u.uid);
        assert_eq!(1, u.gid);
        assert_eq!("/usr/sbin", &u.home);
        assert_eq!("/usr/sbin/nologin", &u.shell);

        let (rem, u) = user("i-have-dashes:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin")
            .ok()
            .unwrap();
        assert!(rem.is_empty());
        assert_eq!("i-have-dashes", &u.name);

        let (rem, u) = user("i_have_underscores:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin")
            .ok()
            .unwrap();
        assert!(rem.is_empty());
        assert_eq!("i_have_underscores", &u.name);
    }

    #[test]
    fn parse_groups_entry() {
        let (rem, g) = group("root:x:0:").ok().unwrap();
        assert!(rem.is_empty());
        assert_eq!("root", &g.name);
        assert_eq!(0, g.gid);
        assert!(g.users.is_empty());

        let (rem, g) = group("tty:x:5:syslog").ok().unwrap();
        assert!(rem.is_empty());
        assert_eq!("tty", &g.name);
        assert_eq!(5, g.gid);
        assert_eq!(vec!["syslog"], g.users);

        let (rem, g) = group("fake:x:999:a,b,c").ok().unwrap();
        assert!(rem.is_empty());
        assert_eq!("fake", &g.name);
        assert_eq!(999, g.gid);
        assert_eq!(vec!["a", "b", "c"], g.users);

        let (rem, g) = group("i-have-dashes:x:999:a").ok().unwrap();
        assert!(rem.is_empty());
        assert_eq!("i-have-dashes", &g.name);

        let (rem, g) = group("i_have_underscores:x:999:a").ok().unwrap();
        assert!(rem.is_empty());
        assert_eq!("i_have_underscores", &g.name);
    }
}
