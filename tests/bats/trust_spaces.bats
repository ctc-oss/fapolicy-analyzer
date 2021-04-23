#!/usr/bin/env bats

export test_name="filenames_with_spaces"

setup() {
  load "helper/podman"
  setup_with_rules ctcoss/fapolicy-analyzer trust.rules
  add "bin/name with spaces.sh"
}

# add the file through the ancillary trust
@test "trust: names with spaces" {
  run in_container "/deny/name with spaces.sh"
  assert_output --partial "permission denied"

  run in_container python3 examples/add_trust.py "/deny/name with spaces.sh"
  assert_output --partial "applying"

  sleep 1

  run in_container python3 examples/show_ancillary.py
  # todo;; expected failure, successful test code follows
  assert_output --partial "0 ancillary trust entries"
  #  assert_output --partial "/deny/name with spaces.sh"
  #
  #  run in_container "/deny/name with spaces.sh"
  #  assert_output "OK"
}

# add the file directly to the lmdb backend
@test "trust: names with spaces - with util" {
  run in_container "/deny/name with spaces.sh"
  assert_output --partial "permission denied"

  run in_container trustdb_add "/deny/name with spaces.sh"

  run in_container python3 examples/show_ancillary.py
  assert_output --partial "/deny/name with spaces.sh"

  run in_container "/deny/name with spaces.sh"
  # todo;; expected failure, successful test code follows
  assert_output --partial "permission denied"
  #  assert_output "OK"
}
