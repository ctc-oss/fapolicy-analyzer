#!/bin/sh
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

if [ $# -lt 2 ]; then
  echo "Usage: $(basename "$0") out_directory image1 [ image2 ... ]"
  exit 1
fi

_output="${1}"
shift

for I in $@; do
  DOCKER_BUILDKIT=1 docker build \
    -o "${_output}" \
    --build-arg platform="$I" \
    --build-arg pyrpm="python3$(echo "$I" | fgrep -q fedora || printf "9")" \
    --build-arg git_commit="$(git describe --match "v*" --abbrev=0 --candidates=0 || git rev-parse --verify HEAD)" \
    --build-arg rpm_version="$(git describe --always --match "v*" | sed -e 's/^v//' -e 's/-rc[0-9]*//' -e 's/-[0-9]\{1,\}-g[0-9a-f]\{1,\}//' -e 's/-/\./g')" \
    --build-arg rpm_release="0$(git describe --always --match "v*" | sed -e 's/[^-]\{1,\}//' -e 's/-/./g')" \
    --build-arg http_proxy="$http_proxy" \
    --build-arg https_proxy="$https_proxy" \
    .
done
