use std::io::Read;

use data_encoding::HEXLOWER;
use ring::digest::{Context, SHA256};

use crate::error::Error;

/// generate a sha256 hash as a string
pub fn sha256_digest<R: Read>(mut reader: R) -> Result<String, Error> {
    let mut context = Context::new(&SHA256);
    let mut buffer = [0; 1024];

    loop {
        let count = reader.read(&mut buffer)?;
        if count == 0 {
            break;
        }
        context.update(&buffer[..count]);
    }

    Ok(HEXLOWER.encode(context.finish().as_ref()))
}

// tested with integration tests
