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


if [[ ! -d /run/fapolicyd ]]; then mkdir /run/fapolicyd; fi
if [[ ! -p /run/fapolicyd/fapolicyd.fifo ]]; then mkfifo /run/fapolicyd/fapolicyd.fifo; fi

chown "$SUDO_UID" /run/fapolicyd/fapolicyd.fifo

while i=$(cat /run/fapolicyd/fapolicyd.fifo); do echo "$i"; done
