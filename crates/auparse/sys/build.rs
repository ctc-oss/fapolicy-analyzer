/*
 * Copyright Concurrent Technologies Corporation 2023
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

extern crate bindgen;

use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    println!("cargo:rustc-link-lib=audit");
    println!("cargo:rustc-link-lib=auparse");
    println!("cargo:rerun-if-changed=wrapper.h");

    let bindings = bindgen::Builder::default()
        .rust_target("1.79.0".parse()?)
        .header("wrapper.h")
        .blocklist_type("timex")
        .parse_callbacks(Box::new(bindgen::CargoCallbacks::new()))
        .generate()
        .expect("Unable to generate bindings");

    bindings
        .write_to_file("src/bindings.rs")
        .expect("Couldn't write bindings!");

    Ok(())
}
