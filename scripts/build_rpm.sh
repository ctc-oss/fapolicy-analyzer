#!/usr/bin/env bash

python setup.py bdist_wheel

mkdir -p "$HOME"/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

cp dist/fapolicy_analyzer-*.whl "$HOME"/rpmbuild/SOURCES

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cp "$SCRIPT_DIR/fapolicy-analyzer.spec" "$HOME"/rpmbuild/SPECS

rpmbuild -ba "$HOME"/rpmbuild/SPECS/fapolicy-analyzer.spec

