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

spec_file="fapolicy-analyzer.spec"

if [[ "$ONLINE" -eq 1 ]]; then
  cd /tmp/rpmbuild/SOURCES
  spectool -gf "../SPECS/$spec_file"
  cd /tmp/rpmbuild/SPECS
  dnf builddep "$spec_file" -y
fi

cd /tmp/rpmbuild/SPECS
rpmbuild -ba "$spec_file"
