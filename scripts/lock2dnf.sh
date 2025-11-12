#!/usr/bin/env bash

# install all available packages for a Cargo.lock
# generate a temporary spec file and use builddep to install

if [ -z "$1" ]; then
  echo "usage: lock2dnf <path-to-cargo-toml>"
  exit 1
fi

tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT

echo "Name: fapolicy-analyzer-builddeps" > "${tmpfile}"
echo "Summary: Cargo2RPM Build Dependencies" | tee -a "${tmpfile}"
echo "Version: 0.0.0" | tee -a "${tmpfile}"
echo "License: None" | tee -a "${tmpfile}"
echo "Release: 1" | tee -a "${tmpfile}"
cargo2rpm --path "$1" buildrequires --with-check --all-features | sed 's/^/BuildRequires: /' | tee -a "${tmpfile}"
echo "%description" | tee -a "${tmpfile}"
dnf builddep -y --enable-repo updates-testing --spec "${tmpfile}"
