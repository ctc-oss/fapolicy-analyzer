#!/usr/bin/env bats
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

export test_name="basic_fapolicyd"

setup() {
  load "helper/podman"
  setup_with_rules ctcoss/fapolicyd simple.rules
  add bin/simple.sh
}

@test "rule: deny script" {
  run in_container /deny/simple.sh
  assert_output --partial "permission denied"
}

@test "rule: allow script" {
  run in_container /allow/simple.sh
  assert_output "OK"
}
