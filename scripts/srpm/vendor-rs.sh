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

set -e

# rust
rm -rf vendor-rs
# the dest path here needs to stay synced up with the path in lock2spec.py
cargo vendor-filterer --platform=x86_64-unknown-linux-gnu vendor-rs/vendor &> /dev/null
python3 scripts/srpm/lock2spec.py
tar czf vendor-rs-${1}.tar.gz -C vendor-rs .

du -sh vendor-rs-${1}.tar.gz
