#!/usr/bin/env bash

rm -rf vendor
cargo vendor-filterer --platform=x86_64-unknown-linux-gnu &> /dev/null
./scripts/srpm/lock2spec.py
tar czf crates.tar.gz -C vendor .
du -sh crates.tar.gz
