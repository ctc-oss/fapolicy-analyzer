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

# rust
rm -rf vendor-rs
cargo vendor-filterer --platform=x86_64-unknown-linux-gnu vendor-rs &> /dev/null
./scripts/srpm/lock2spec.py
mkdir vendor-tmp
mv vendor-rs vendor-tmp/vendor
mv vendor-tmp vendor-rs
tar czf vendor-rs.tar.gz -C vendor-rs .

du -sh vendor-rs.tar.gz
