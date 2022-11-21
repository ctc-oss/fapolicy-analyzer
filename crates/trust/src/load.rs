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

// todo;; thiserr
fn from_dir(from: &Path) -> Result<(), io::Error> {
    let d_files = read_sorted_d_files(from)?;

    Ok(())
}

pub(crate) type TrustSource = (PathBuf, String);

fn trust_file(path: PathBuf) -> Result<Vec<TrustSource>, io::Error> {
    let reader = File::open(&path).map(BufReader::new)?;
    let lines = reader
        .lines()
        .flatten()
        .map(|s| (path.clone(), s))
        .collect();
    Ok(lines)
}

fn read_sorted_d_files(from: &Path) -> Result<Vec<PathBuf>, io::Error> {
    let d_files: Result<Vec<PathBuf>, io::Error> =
        fs::read_dir(from)?.map(|e| e.map(|e| e.path())).collect();

    let mut d_files: Vec<PathBuf> = d_files?
        .into_iter()
        .filter(|p| p.is_file() && p.display().to_string().ends_with(".rules"))
        .collect();

    d_files.sort_by_key(|p| p.display().to_string());

    Ok(d_files)
}
