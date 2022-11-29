use fapolicy_trust::db::Entry;
use fapolicy_trust::load::{from_dir, from_file, load_from_file, read_sorted_d_files};
use std::error::Error;
use std::path::PathBuf;

fn main() -> Result<(), Box<dyn Error>> {
    let db = load_from_file(
        &PathBuf::from("/etc/fapolicyd/trust.d"),
        Some(&PathBuf::from("/etc/fapolicyd/fapolicyd.trust")),
    )?;
    dbg!(db);
    // for (origin, text) in from_dir(&PathBuf::from("/etc/fapolicyd/trust.d"))? {
    //     match parse_trust_record(&text) {
    //         Ok(x) => {
    //             dbg!(Entry::Valid(x));
    //         }
    //         Err(e) if !text.is_empty() => {
    //             dbg!(Entry::Invalid {
    //                 text,
    //                 error: format!("{e:?}")
    //             });
    //         }
    //         _ => {}
    //     };
    // }

    Ok(())
}
