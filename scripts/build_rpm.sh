#!/usr/bin/env bash

#python setup.py bdist_wheel

ver=$1

#rm -rf "$HOME"/rpmbuild
#mkdir -p "$HOME"/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

#cp dist/fapolicy_analyzer-*.whl "$HOME"/rpmbuild/SOURCES
#cp "$HOME/Downloads/fapolicy-analyzer-master.zip" "$HOME"/rpmbuild/SOURCES

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cp "$SCRIPT_DIR/fapolicy-analyzer$ver.spec" "$HOME"/rpmbuild/SPECS/fapolicy-analyzer.spec

rpmbuild -ba "$HOME"/rpmbuild/SPECS/fapolicy-analyzer.spec
pip
