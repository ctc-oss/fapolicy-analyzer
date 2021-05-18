#!/usr/bin/env bats

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

  sleep 1

  run in_container python3 examples/show_ancillary.py
  # todo;; expected failure, successful test code follows
  assert_output --partial "0 ancillary trust entries"
  #  assert_output --partial "/deny/ÀÆ.sh"
  #
  #  run in_container "/deny/ÀÆ.sh"
  #  assert_output "OK"
}

# add the file directly to the lmdb backend
@test "trust: uft-8 names - with util" {
  run in_container "/deny/ÀÆ.sh"
  assert_output --partial "permission denied"

  run in_container trustdb_add "/deny/ÀÆ.sh"

  run in_container python3 examples/show_ancillary.py
  assert_output --partial "/deny/ÀÆ.sh"

  run in_container "/deny/ÀÆ.sh"
  # todo;; expected failure, successful test code follows
  assert_output --partial "permission denied"
  #  assert_output "OK"
}
