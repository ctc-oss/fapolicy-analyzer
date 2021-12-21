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

readonly rules=$1
readonly config=fapolicyd.conf
readonly allowdir=/tmp/allow
readonly denydir=/tmp/deny

mkdir $allowdir $denydir
cp /bin/ls $allowdir
cp /bin/ls $denydir

readonly cname=testing-fapolicyd-runsh

sudo podman run -d --name $cname --rm -it \
              --privileged \
              -v "$PWD/$rules:/etc/fapolicyd/fapolicyd.rules" \
              -v "$PWD/$config:/etc/fapolicyd/fapolicyd.conf" \
              -v "$allowdir:/allow" \
              -v "$denydir:/deny"  \
              ctcoss/fapolicyd

sudo podman exec -it $cname groupadd -g 12345 test
sudo podman exec -it $cname useradd -g 12345 -u 10001 tester

sudo podman exec -u 10001 -it $cname bash

sudo podman exec -it $cname journalctl -u fapolicyd

sudo podman kill $cname

echo "done"
