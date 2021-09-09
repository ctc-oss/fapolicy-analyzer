// use std::collections::HashMap;
// use std::fs::File;
// use std::io::prelude::*;
// use std::io::BufReader;
// use std::path::Path;
//
// use lmdb::{Cursor, Environment, Transaction};
// use thiserror::Error;
//
// use crate::error;
// use crate::error::Error::FileNotFound;
// use crate::sha::sha256_digest;
// use crate::trust::Error::{
//     LmdbNotFound, LmdbPermissionDenied, LmdbReadFail, MalformattedTrustEntry, UnsupportedTrustType,
// };
// use crate::trust::TrustOp::{Add, Del};
// use fapolicy_trust::trust::TrustSource::Ancillary;
// use fapolicy_trust::Trust;
//
// struct TrustPair {
//     k: String,
//     v: String,
// }
//
// #[cfg(test)]
// mod tests {
//     use super::*;
//
//     #[test]
//     fn parse_record() {
//         let s =
//             "/home/user/my-ls 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87";
//         let e = parse_trust_record(s).unwrap();
//         assert_eq!(e.path, "/home/user/my-ls");
//         assert_eq!(e.size, 157984);
//         assert_eq!(
//             e.hash,
//             "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
//         );
//     }
//
//     #[test]
//     fn parse_record_with_space() {
//         let s =
//             "/home/user/my ls 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87";
//         let e = parse_trust_record(s).unwrap();
//         assert_eq!(e.path, "/home/user/my ls");
//         assert_eq!(e.size, 157984);
//         assert_eq!(
//             e.hash,
//             "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
//         );
//     }
//
//     #[test]
//     // todo;; additional coverage for type 2 and invalid type
//     fn parse_trust_pair() {
//         let tp = TrustPair::new((
//             "/home/user/my-ls".as_bytes(),
//             "1 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87".as_bytes(),
//         ));
//         let t: Trust = tp.into();
//
//         assert_eq!(t.path, "/home/user/my-ls");
//         assert_eq!(t.size, 157984);
//         assert_eq!(
//             t.hash,
//             "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
//         );
//     }
//
//     fn make_trust(path: &str, size: u64, hash: &str) -> Trust {
//         Trust {
//             path: path.to_string(),
//             size,
//             hash: hash.to_string(),
//             source: TrustSource::Ancillary,
//         }
//     }
//
//     fn make_default_trust_at(path: &str) -> Trust {
//         Trust {
//             path: path.to_string(),
//             ..make_default_trust()
//         }
//     }
//
//     fn make_default_trust() -> Trust {
//         make_trust(
//             "/home/user/my_ls",
//             157984,
//             "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87",
//         )
//     }
//
//     #[test]
//     fn changeset_simple() {
//         let expected = make_default_trust();
//
//         let mut xs = Changeset::new();
//         xs.ins(&*expected.path, expected.size, &*expected.hash);
//         assert_eq!(xs.len(), 1);
//
//         let store = xs.apply(HashMap::new());
//         assert_eq!(store.len(), 1);
//
//         let actual = store.get(&expected.path).unwrap();
//         assert_eq!(*actual, expected);
//     }
//
//     #[test]
//     fn changeset_multiple_changes() {
//         let mut xs = Changeset::new();
//         xs.ins("/foo/bar", 1000, "12345");
//         xs.ins("/foo/fad", 1000, "12345");
//         assert_eq!(xs.len(), 2);
//
//         let store = xs.apply(HashMap::new());
//         assert_eq!(store.len(), 2);
//     }
//
//     #[test]
//     fn changeset_del_existing() {
//         let mut existing = HashMap::new();
//         existing.insert("/foo/bar".to_string(), make_default_trust_at("/foo/bar"));
//         assert_eq!(existing.len(), 1);
//
//         let mut xs = Changeset::new();
//         xs.del("/foo/bar");
//         assert_eq!(xs.len(), 1);
//
//         let store = xs.apply(existing);
//         assert_eq!(store.len(), 0);
//     }
//
//     #[test]
//     fn changeset_add_then_del() {
//         let mut xs = Changeset::new();
//         xs.ins("/foo/bar", 1000, "12345");
//         assert_eq!(xs.len(), 1);
//
//         xs.del("/foo/bar");
//         assert_eq!(xs.len(), 2);
//
//         let store = xs.apply(HashMap::new());
//         assert_eq!(store.len(), 0);
//     }
//
//     #[test]
//     fn changeset_multiple_changes_same_file() {
//         let expected = make_default_trust();
//
//         let mut xs = Changeset::new();
//         xs.ins(&*expected.path, 1000, "12345");
//         assert_eq!(xs.len(), 1);
//         xs.ins(&*expected.path, expected.size, &*expected.hash);
//
//         let store = xs.apply(HashMap::new());
//         assert_eq!(store.len(), 1);
//
//         let actual = store.get(&expected.path).unwrap();
//         assert_eq!(*actual, expected);
//     }
// }
