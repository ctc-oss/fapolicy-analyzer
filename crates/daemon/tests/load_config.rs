use std::fs::File;
use std::io::BufReader;

fn parse_default_config() {
    let f = File::open("tests/data/default.conf").expect("open file");
    let buff = BufReader::new(f);
}
