use std::fs::File;
use std::io::BufReader;

use fapolicy_util::sha::sha256_digest;

#[test]
fn test_hashme() {
    let expected = "047bc85db1001a7c98c13f594178d339efc60e3b099af5d27a65498ddc808f55";
    let f = File::open("tests/data/hashme.txt").expect("failed to open file");
    let actual = sha256_digest(BufReader::new(&f)).expect("failed to hash file");
    assert_eq!(actual, expected);
}
