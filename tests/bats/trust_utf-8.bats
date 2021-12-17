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

export test_name="utf-8_filenames"

setup() {
  load "helper/podman"
  setup_with_rules ctcoss/fapolicy-analyzer trust.rules
  add "bin/ÀÆ.sh"
}

# add the file through the ancillary trust
@test "trust: uft-8 names" {
  run in_container "/deny/ÀÆ.sh"
  assert_output --partial "permission denied"

  run in_container python3 examples/add_trust.py "/deny/ÀÆ.sh"
  assert_output --partial "applying"
  assert_output --partial "signaling"

  sleep 1

  run in_container python3 examples/show_ancillary.py
  assert_output --partial "/deny/ÀÆ.sh"

  run in_container "/deny/ÀÆ.sh"
  assert_output "OK"
}
