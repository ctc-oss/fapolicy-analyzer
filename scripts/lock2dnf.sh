#!/usr/bin/env bash

# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
