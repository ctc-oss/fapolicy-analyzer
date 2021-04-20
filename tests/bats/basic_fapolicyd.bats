#!/usr/bin/env bats

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
