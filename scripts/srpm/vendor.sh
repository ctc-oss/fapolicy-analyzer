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

rm -rf vendor
cargo vendor-filterer --platform=x86_64-unknown-linux-gnu &> /dev/null
./scripts/srpm/lock2spec.py
tar czf crates.tar.gz -C vendor .
curl -sL -o /tmp/semanticversion.tar.gz https://github.com/rbarrois/python-semanticversion/archive/refs/tags/2.10.0.tar.gz
git clone https://github.com/PyO3/setuptools-rust.git -b v1.1.2
mkdir /tmp/____Extract
tar xzf /tmp/setuptools-rust.tar.gz -C /tmp/____Extract
tar xzf /tmp/semanticversion.tar.gz -C /tmp/____Extract
tar czf python.tar.gz -C /tmp/____Extract .
rm -rf /tmp/____Extract
du -sh crates.tar.gz
du -sh python.tar.gz
