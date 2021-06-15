#!/usr/bin/env bash

readonly describe=${DESCRIBE:-$(cat DESCRIBE)}
readonly version=${VERSION:-$(cat VERSION)}
readonly release=${RELEASE:-$(cat RELEASE)}
readonly output_dir=${1:-"/output"}

set_cargo_version() {
  sed -i -e "0,/version = \".*\"/ s/version = \".*\"/version = \"$describe\"/; t" "$1"
}

main() {
  mkdir -p "$HOME"/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

  set_cargo_version Cargo.toml
  set_cargo_version ../Cargo.toml
  VERSION="$version" python setup.py bdist_wheel

  cp bin/fapolicy-analyzer        "$HOME"/rpmbuild/SOURCES
  cp dist/fapolicy_analyzer-*.whl "$HOME"/rpmbuild/SOURCES

  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
  cp "$SCRIPT_DIR/fapolicy-analyzer.spec" "$HOME"/rpmbuild/SPECS

  rpmbuild -ba -D "version $version" -D "release $release" "$HOME"/rpmbuild/SPECS/fapolicy-analyzer.spec

  mv "$HOME"/rpmbuild/RPMS/*/* "$output_dir"
  mv "$HOME"/rpmbuild/SRPMS/*  "$output_dir"
}

main "$@"
