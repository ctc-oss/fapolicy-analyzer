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

echo "[build.sh] mock $1"
mock -r "$1" --init
mock -r "$1" --resultdir ${rpmbuild_dir} --buildsrpm --sources ${rpmbuild_dir}/SOURCES/ --spec ${rpmbuild_dir}/SPECS/${spec_file}
mock -r "$1" --resultdir ${rpmbuild_dir} --rebuild ${rpmbuild_dir}/*.src.rpm

if [[ -n "$2" ]]; then
  echo "[build.sh] exporting rpms to ${2}"
  cp -v ${rpmbuild_dir}/*.rpm ${2}
  cp -v ${rpmbuild_dir}/*.rpm ${2}
fi
