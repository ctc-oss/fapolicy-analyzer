use rpm::db::Database;

fn main() {
    let db = Database::load();
    for x in db.files {
        println!("{:?}", x);
    }

    println!("v0.0.4");
}
