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
rpmbuild_dir=/tmp/rpmbuild

if [[ "$ONLINE" -eq 1 ]]; then
  cd ${rpmbuild_dir}/SOURCES
  spectool -g "../SPECS/$spec_file"
  cd ${rpmbuild_dir}/SPECS
  dnf builddep "$spec_file" -y
fi

cd ${rpmbuild_dir}/SPECS
rpmbuild -ba "$spec_file" -D "_topdir ${rpmbuild_dir}"

if [[ ! -z "$1" ]]; then
  echo "[build.sh] exporting *rpms to ${1}"
  cp -v ${rpmbuild_dir}/RPMS/**/*.rpm ${1}
  cp -v ${rpmbuild_dir}/SRPMS/*.rpm   ${1}
fi
