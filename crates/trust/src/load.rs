use crate::db::{Rec, DB};
use crate::error::Error;
use crate::read::parse_trust_record;
use crate::Trust;
use std::collections::hash_map::Entry;
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::{fs, io};

// load all trust files
// load all entries from all files
// write to mutable map with a single entry from each row
//  -- can add diagnostic messages to the entries to flag if they overwrote a dupe
// compare with lmdb, adding diagnostics for anything that is out of sync

fn from_db() {}

pub(crate) type TrustSourceEntry = (PathBuf, String);

// path to d dir (/etc/fapolicyd/trust.d), optional override file (eg /etc/fapolicyd/fapolicyd.trust
pub fn load_trust_db(d: &Path, o: Option<&Path>) -> Result<DB, Error> {
    let mut d_entries = from_dir(d)?;
    let mut o_entries = if let Some(f) = o {
        from_file(f)?
    } else {
        vec![]
    };
    d_entries.append(&mut o_entries);

    let parsed: Vec<(String, Trust)> = d_entries
        .iter()
        // todo;; support comments elsewhere
        .filter(|(_, txt)| !txt.is_empty() || txt.trim_start().starts_with("#"))
        .map(|(p, txt)| (p.display().to_string(), parse_trust_record(txt.trim())))
        .filter(|(_, r)| r.is_ok())
        .map(|(p, r)| (p, r.unwrap()))
        .collect();

    let mut entries: HashMap<String, Rec> = HashMap::default();
    for (o, t) in parsed {
        match entries.entry(t.path.clone()) {
            Entry::Occupied(e) => {
                eprintln!("duplicated trust record")
            }
            Entry::Vacant(e) => {
                let mut rec = Rec::new(t);
                rec.origin = Some(o);
                e.insert(rec);
            }
        }
    }

    Ok(entries.into())
}

pub fn from_file(from: &Path) -> Result<Vec<TrustSourceEntry>, io::Error> {
    let r = BufReader::new(File::open(&from)?);
    let lines: Result<Vec<String>, io::Error> = r.lines().collect();
    Ok(lines?
        .iter()
        .map(|l| (PathBuf::from(from), l.clone()))
        .collect())
}

// todo;; thiserr
pub fn from_dir(from: &Path) -> Result<Vec<TrustSourceEntry>, io::Error> {
    let d_files = read_sorted_d_files(from)?;

    let d_files: Result<Vec<(PathBuf, File)>, io::Error> = d_files
        .into_iter()
        .map(|p| (p.clone(), File::open(&p)))
        .map(|(p, r)| r.map(|f| (p, f)))
        .collect();

    let d_files = d_files?.into_iter().map(|(p, f)| (p, BufReader::new(f)));

    // todo;; externalize result flattening via expect here
    let d_files = d_files.into_iter().map(|(path, rdr)| {
        (
            path.clone(),
            rdr.lines()
                .collect::<Result<Vec<String>, io::Error>>()
                .unwrap_or_else(|_| {
                    panic!("failed to read lines from trust file, {}", path.display())
                }),
        )
    });

    let d_files: Vec<TrustSourceEntry> = d_files
        .into_iter()
        .flat_map(|(src, lines)| {
            lines
                .iter()
                .map(|l| (src.clone(), l.clone()))
                .collect::<Vec<TrustSourceEntry>>()
        })
        .collect();

    Ok(d_files)
}

fn trust_file(path: PathBuf) -> Result<Vec<TrustSourceEntry>, io::Error> {
    let reader = File::open(&path).map(BufReader::new)?;
    let lines = reader
        .lines()
        .flatten()
        .map(|s| (path.clone(), s))
        .collect();
    Ok(lines)
}

pub fn read_sorted_d_files(from: &Path) -> Result<Vec<PathBuf>, io::Error> {
    let d_files: Result<Vec<PathBuf>, io::Error> =
        fs::read_dir(from)?.map(|e| e.map(|e| e.path())).collect();

    let mut d_files: Vec<PathBuf> = d_files?
        .into_iter()
        .filter(|p| p.is_file() && p.display().to_string().ends_with(".trust"))
        .collect();

    d_files.sort_by_key(|p| p.display().to_string());

    Ok(d_files)
}
