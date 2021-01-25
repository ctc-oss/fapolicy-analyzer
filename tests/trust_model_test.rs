use std::str::FromStr;

use fapolicyd::trust::TrustEntry;

#[test]
fn deserialize_entry() {
    let s =
        "/home/user/my-ls 157984 61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87";
    let e = TrustEntry::from_str(s).unwrap();
    assert_eq!(e.path, "/home/user/my-ls");
    assert_eq!(e.size, 157984);
    assert_eq!(
        e.hash,
        "61a9960bf7d255a85811f4afcac51067b8f2e4c75e21cf4f2af95319d4ed1b87"
    );
}
