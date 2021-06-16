use std::fs::metadata;
use std::fs::File;
use std::io::BufReader;
use std::path::Path;

use fapolicy_analyzer::*;
use sha::sha256_digest;
use trust::load_trust_db;

fn main() {
    let path = "/usr/local/data2/dev/code/isis/fapolicy-analyzer/.local/fapolicyd-db";
    let tdb = load_trust_db(path);

    tdb.iter().for_each(|t| {
        match File::open(&t.path) {
            Ok(f) => {
                let meta = metadata(Path::new(&t.path));
                match sha256_digest(BufReader::new(f)) {
                    Ok(sha) => {
                        println!(
                            "sha: {} {} {} {}",
                            sha,
                            t.path,
                            t.hash == sha,
                            meta.unwrap().len()
                        );
                    }
                    Err(_) => println!("sha failed"),
                }
            }
            _ => println!("WARN: {} not found", t.path),
        };
    })
}
