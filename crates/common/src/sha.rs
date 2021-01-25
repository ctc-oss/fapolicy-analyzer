use std::io::{Read, Result};

use data_encoding::HEXUPPER;
use ring::digest::{Context, SHA256};

// sha example from cookbook
pub fn sha256_digest<R: Read>(mut reader: R) -> Result<String> {
    let mut context = Context::new(&SHA256);
    let mut buffer = [0; 1024];

    loop {
        let count = reader.read(&mut buffer)?;
        if count == 0 {
            break;
        }
        context.update(&buffer[..count]);
    }

    Ok(HEXUPPER.encode(context.finish().as_ref()))
}
