#!/usr/bin/env bash
#
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


mkdir /tmp/bats
cd /tmp/bats || exit 1
curl -Lo bats.tar.gz https://github.com/bats-core/bats-core/archive/refs/tags/v1.3.0.tar.gz
curl -Lo bats-assert.tar.gz https://github.com/bats-core/bats-assert/archive/refs/tags/v2.0.0.tar.gz
curl -Lo bats-support.tar.gz https://github.com/bats-core/bats-support/archive/refs/tags/v0.3.0.tar.gz
for gz in *.gz; do tar xvzf $gz; done

cd bats-core-* || exit 1
./install.sh "$HOME/.local"
cd -

mkdir -p "$HOME/.local/share/bats/assert"
mkdir -p "$HOME/.local/share/bats/support"

cp -r bats-assert-*/* "$HOME/.local/share/bats/assert"
cp -r bats-support-*/* "$HOME/.local/share/bats/support"

rm -rf /tmp/bats*
