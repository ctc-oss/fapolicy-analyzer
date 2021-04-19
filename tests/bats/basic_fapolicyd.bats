#!/usr/bin/env bats

test_name="test_example"
test_image="ctcoss/fapolicyd"
podman_cmd="sudo podman"
voldir=/tmp/$test_name
bats_test_dir="$BATS_CWD/tests/bats"
bats_load_dir="$BATS_ROOT/share/bats"

setup() {
  load "$bats_load_dir/assert/load.bash"
  load "$bats_load_dir/support/load.bash"

  sleep 1
  mkdir -p "$voldir"
  $podman_cmd run -d --name "$test_name" --rm -it \
                     --privileged --entrypoint='' \
                     -v "$bats_test_dir/etc/simple.rules:/etc/fapolicyd/fapolicyd.rules" \
                     -v "$voldir:/allow" -v "$voldir:/deny" \
                     "$test_image" fapolicyd --debug

  cp "$bats_test_dir/bin/simple.sh" "$voldir"
  sleep 1
}

teardown() {
  $podman_cmd kill "$test_name"
  rm -rf "$voldir"
}

# todo;; move the above into shared location
# ==========================================

@test "rule: deny script" {
  run $podman_cmd exec -it $test_name /deny/simple.sh
  assert_output --partial "permission denied"
}

@test "rule: allow script" {
  run $podman_cmd exec -it $test_name /allow/simple.sh
  assert_output "OK"
}
