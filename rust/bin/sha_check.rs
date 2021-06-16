use std::fs::metadata;
use std::fs::File;
use std::io::BufReader;
use std::io::Result;
use std::path::Path;

use fapolicy_analyzer::*;
use sha::sha256_digest;

fn main() -> Result<()> {
    let p = "/bin/ls";
    let f = File::open(p)?;
    let meta = metadata(Path::new(p));
    let sha = sha256_digest(BufReader::new(f))?;
    println!("sha: {} {}", sha, meta.unwrap().len());

    Ok(())
}
