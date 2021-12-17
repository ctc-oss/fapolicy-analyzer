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


export test_name="basic_trust"

setup() {
  load "helper/podman"
  setup_with_rules ctcoss/fapolicy-analyzer trust.rules
  add bin/simple.sh
}

@test "trust: add" {
  # initially denied :thumbs_down:
  run in_container /deny/simple.sh
  assert_output --partial "permission denied"

  # trust the script
  run in_container python3 examples/add_trust.py /deny/simple.sh
  assert_output --partial "applying"
  assert_output --partial "signaling"

  # give fapolicyd a second to update
  sleep 1

  # check the db for the script
  run in_container python3 examples/show_ancillary.py
  assert_output --partial "/deny/simple.sh"

  # now its runs :thumbs_up:
  run in_container /deny/simple.sh
  assert_output "OK"
}
