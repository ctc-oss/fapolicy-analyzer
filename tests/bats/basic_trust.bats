#!/usr/bin/env bats

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

  # check the db for the script
  run in_container python3 examples/show_ancillary.py
  assert_output --partial "/deny/simple.sh"

  # now its runs :thumbs_up:
  run in_container /deny/simple.sh
  assert_output "OK"
}
