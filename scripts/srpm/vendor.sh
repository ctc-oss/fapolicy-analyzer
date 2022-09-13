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

# python
rm -rf vendor-py && mkdir vendor-py && cd vendor-py
curl -sLO https://github.com/pypa/pip/archive/refs/tags/21.3.1.tar.gz
curl -sLO https://github.com/pypa/setuptools/archive/refs/tags/v59.6.0.tar.gz
curl -sLO https://github.com/rbarrois/python-semanticversion/archive/refs/tags/2.8.2.tar.gz
for f in *.tar.gz; do tar xzf ${f}; rm ${f}; done
for d in ./*; do mv ${d} $(echo ${d} | rev | cut -d- -f2- | rev); done
git clone https://github.com/PyO3/setuptools-rust.git -b v1.1.2 &> /dev/null

cd ..
tar czf vendor-py.tar.gz -C vendor-py .

du -sh vendor-rs.tar.gz
du -sh vendor-py.tar.gz
