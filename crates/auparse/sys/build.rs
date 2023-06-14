extern crate bindgen;

fn main() {
    println!("cargo:rustc-link-lib=audit");
    println!("cargo:rustc-link-lib=auparse");
    println!("cargo:rerun-if-changed=wrapper.h");

    let bindings = bindgen::Builder::default()
        .header("wrapper.h")
        .blocklist_type("timex")
        .parse_callbacks(Box::new(bindgen::CargoCallbacks))
        .generate()
        .expect("Unable to generate bindings");

    bindings
        .write_to_file("src/bindings.rs")
        .expect("Couldn't write bindings!");
}
