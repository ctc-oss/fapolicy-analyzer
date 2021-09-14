use crate::ops::TrustOp::{Add, Del};
use crate::source::TrustSource::Ancillary;
use fapolicy_api::trust::Trust;
use fapolicy_util::sha::sha256_digest;
use std::collections::HashMap;
use std::fs::File;
use std::io::BufReader;

#[derive(Clone, Debug)]
enum TrustOp {
    Add(String),
    Del(String),
    Ins(String, u64, String),
}

impl TrustOp {
    fn run(&self, trust: &mut HashMap<String, Trust>) -> Result<(), String> {
        match self {
            TrustOp::Add(path) => match new_trust_record(path) {
                Ok(t) => {
                    trust.insert(path.to_string(), t);
                    Ok(())
                }
                Err(_) => Err("failed to add trust".to_string()),
            },
            TrustOp::Ins(path, size, hash) => {
                trust.insert(
                    path.clone(),
                    Trust {
                        path: path.to_string(),
                        size: *size,
                        hash: hash.clone(),
                    },
                );
                Ok(())
            }
            TrustOp::Del(path) => {
                trust.remove(path);
                Ok(())
            }
        }
    }
}

fn to_pair(trust_op: &TrustOp) -> (String, String) {
    match trust_op {
        TrustOp::Add(path) => (path.to_string(), "Add".to_string()),
        TrustOp::Del(path) => (path.to_string(), "Del".to_string()),
        TrustOp::Ins(path, _size, _hash) => (path.to_string(), "Ins".to_string()),
    }
}

pub enum ChangesetErr {
    NotFound,
}

/// mutable append-only container for change operations
#[derive(Clone, Debug)]
pub struct Changeset {
    changes: Vec<TrustOp>,
}

impl Changeset {
    pub fn new() -> Self {
        Changeset { changes: vec![] }
    }

    /// generate a modified trust map
    pub fn apply(&self, trust: HashMap<String, Trust>) -> HashMap<String, Trust> {
        let mut modified = trust;
        for change in self.changes.iter() {
            change.run(&mut modified).unwrap()
        }
        modified
    }

    pub fn add(&mut self, path: &str) {
        self.changes.push(Add(path.to_string()))
    }

    pub fn del(&mut self, path: &str) {
        self.changes.push(Del(path.to_string()))
    }

    pub fn len(&self) -> usize {
        self.changes.len()
    }

    pub fn is_empty(&self) -> bool {
        self.changes.is_empty()
    }
}

pub fn get_path_action_map(cs: &Changeset) -> HashMap<String, String> {
    cs.changes.iter().map(to_pair).collect()
}

impl ::std::default::Default for Changeset {
    fn default() -> Self {
        Self { changes: vec![] }
    }
}

fn new_trust_record(path: &str) -> Result<Trust, String> {
    let f = File::open(path).map_err(|_| "failed to open file".to_string())?;
    let sha = sha256_digest(BufReader::new(&f)).map_err(|_| "failed to hash file".to_string())?;

    Ok(Trust {
        path: path.to_string(),
        size: f.metadata().unwrap().len(),
        hash: sha,
    })
}

trait InsChange {
    fn ins(&mut self, path: &str, size: u64, hash: &str);
}

impl InsChange for Changeset {
    fn ins(&mut self, path: &str, size: u64, hash: &str) {
        self.changes
            .push(TrustOp::Ins(path.to_string(), size, hash.to_string()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::source::TrustSource::Ancillary;
    use std::collections::HashMap;

    fn make_trust(path: &str, size: u64, hash: &str) -> Trust {
        Trust {
            path: path.to_string(),
            size,
            hash: hash.to_string(),
        }
    }

    fn make_default_trust_at(path: &str) -> Trust {
        Trust {
            path: path.to_string(),
            ..make_default_trust()
        }
    }

    fn make_default_trust() -> Trust {
        make_trust(
            "/home/user/my_ls",
            157984,
            "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87",
        )
    }

    #[test]
    fn changeset_simple() {
        let expected = make_default_trust();

        let mut xs = Changeset::new();
        xs.ins(&*expected.path, expected.size, &*expected.hash);
        assert_eq!(xs.len(), 1);

        let store = xs.apply(HashMap::new());
        assert_eq!(store.len(), 1);

        let actual = store.get(&expected.path).unwrap();
        assert_eq!(*actual, expected);
    }

    #[test]
    fn changeset_multiple_changes() {
        let mut xs = Changeset::new();
        xs.ins("/foo/bar", 1000, "12345");
        xs.ins("/foo/fad", 1000, "12345");
        assert_eq!(xs.len(), 2);

        let store = xs.apply(HashMap::new());
        assert_eq!(store.len(), 2);
    }

    #[test]
    fn changeset_del_existing() {
        let mut existing = HashMap::new();
        existing.insert("/foo/bar".to_string(), make_default_trust_at("/foo/bar"));
        assert_eq!(existing.len(), 1);

        let mut xs = Changeset::new();
        xs.del("/foo/bar");
        assert_eq!(xs.len(), 1);

        let store = xs.apply(existing);
        assert_eq!(store.len(), 0);
    }

    #[test]
    fn changeset_add_then_del() {
        let mut xs = Changeset::new();
        xs.ins("/foo/bar", 1000, "12345");
        assert_eq!(xs.len(), 1);

        xs.del("/foo/bar");
        assert_eq!(xs.len(), 2);

        let store = xs.apply(HashMap::new());
        assert_eq!(store.len(), 0);
    }

    #[test]
    fn changeset_multiple_changes_same_file() {
        let expected = make_default_trust();

        let mut xs = Changeset::new();
        xs.ins(&*expected.path, 1000, "12345");
        assert_eq!(xs.len(), 1);
        xs.ins(&*expected.path, expected.size, &*expected.hash);

        let store = xs.apply(HashMap::new());
        assert_eq!(store.len(), 1);

        let actual = store.get(&expected.path).unwrap();
        assert_eq!(*actual, expected);
    }
}
