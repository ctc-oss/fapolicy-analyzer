# test_name must be set
if [[ -z "$test_name" ]]; then
  echo "test_name was not defined"
  exit 1
fi

voldir="/tmp/$test_name"
bats_test_dir="$BATS_CWD/tests/bats"
the_podman=$(command -v podman)

# hide podman impl details
podman() {
  sudo "$the_podman" "$@"
}

# run command in the test container
in_container() {
  podman exec -it "$test_name" "$@"
}

# add file to the volume
add() {
  local f="$1"
  cp "$bats_test_dir/$1" "$voldir"
}

# setup the test with a rules entry
setup_with_rules() {
  local bats_load_dir="$BATS_ROOT/share/bats"
  load "$bats_load_dir/assert/load.bash"
  load "$bats_load_dir/support/load.bash"

  bats_test_dir="$BATS_CWD/tests/bats"

  local image="$1"
  local rules="$2"

  sleep 1
  mkdir -p "$voldir"

  podman run -d --name "$test_name" --rm -it \
                     --privileged --entrypoint='' \
                     -v "$bats_test_dir/etc/$rules:/etc/fapolicyd/fapolicyd.rules" \
                     -v "$voldir:/allow" -v "$voldir:/deny" \
                     "$image" fapolicyd --debug
  sleep 1
}

# teardown deleting the volume host dir
teardown() {
  podman kill "$test_name"
  rm -rf "$voldir"
  sleep 1
}
