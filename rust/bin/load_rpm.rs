use fapolicy_analyzer::rpm;

fn main() {
    let t = rpm::load_system_trust("/var/lib/rpm");
    t.iter().for_each(|e| println!("{}", e.path));
    println!("entries: {}", t.len())
}
