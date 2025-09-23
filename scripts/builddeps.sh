#!/usr/bin/env bash

# arg 1: Cargo.toml

echo "Name: fapolicy-analyzer-builddeps" > /tmp/foo.spec
echo "Summary: Cargo2RPM Build Dependencies" >> /tmp/foo.spec
echo "Version: 0.0.0" >> /tmp/foo.spec
echo "License: None" >> /tmp/foo.spec
echo "Release: 1" >> /tmp/foo.spec
cargo2rpm --path "$1" buildrequires | sed 's/^/BuildRequires: /' >> /tmp/foo.spec
echo "%description" >> /tmp/foo.spec
cat /tmp/foo.spec
dnf builddep --spec /tmp/foo.spec
rm /tmp/foo.spec
