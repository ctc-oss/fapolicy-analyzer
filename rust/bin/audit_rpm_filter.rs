use fapolicy_analyzer::fapolicyd::TRUST_DB_PATH;
use fapolicy_analyzer::rpm;
use fapolicy_analyzer::trust::load_trust_db;

fn main() {
    let r = rpm::load_system_trust("/var/lib/rpm");
    let t = load_trust_db(TRUST_DB_PATH);

    // show entries that are in rpm db parse but not in the trust as provided by fapolicyd
    // this show the different in filtering from our rpm load and the fapolicyd rpm load
    for e in r {
        match t.iter().find(|x| x.path == e.path) {
            None => println!("diff: {}", e.path),
            _ => (),
        }
    }
}
