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
vendor_dest=vendor-rs/vendor

id=$(. /etc/os-release && echo $ID)

case $id in
  fedora)
    echo "fedora: vendoring packages"
    mkdir -p ${vendor_dest}
    cp -r /usr/share/cargo/registry/* ${vendor_dest}
    uv run --only-group vendor scripts/srpm/lock2spec.py --vendor_dir=${vendor_dest}
    find ${vendor_dest} -maxdepth 1 -type d -exec touch {}/{README.md,PLATFORM.md,CHANGELOG.md,DESIGN.md} \;
    ;;

  ubuntu)
    echo "ubuntu: vendoring crates.io"
    cargo check
    cargo vendor-filterer --platform=x86_64-unknown-linux-gnu ${vendor_dest} &> /dev/null
    uv run --only-group vendor scripts/srpm/lock2spec.py --vendor_dir=${vendor_dest}
    ;;

  *)
    echo "error: $id is an unsupported build platform"
    ;;
esac


vendor_tar=vendor-rs.tar.gz
vendor_root=$(dirname ${vendor_dest})
tar czf ${vendor_tar} -C ${vendor_root} .

if [[ ! -z "$1" ]]; then
  vendor_tar=vendor-rs-${1}.tar.gz
  mv vendor-rs.tar.gz ${vendor_tar}
fi

du -sh ${vendor_tar}
