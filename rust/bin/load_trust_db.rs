use fapolicy_analyzer::trust::load_trust_db;

fn main() {
    let t = load_trust_db("/home/wassj/dev/code/isis/fapolicy-analyzer/.local/fapolicyd-db");
    println!("entries: {}", t.len())
}
