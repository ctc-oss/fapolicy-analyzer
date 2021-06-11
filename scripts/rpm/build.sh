#!/usr/bin/env bash

readonly version=${VERSION:-$(cat VERSION)}
readonly release=${RELEASE:-$(cat RELEASE)}

mkdir -p "$HOME"/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

VERSION="$version" python setup.py bdist_wheel

cp dist/fapolicy_analyzer-*.whl "$HOME"/rpmbuild/SOURCES

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cp "$SCRIPT_DIR/fapolicy-analyzer.spec" "$HOME"/rpmbuild/SPECS

rpmbuild -ba -D "version $version" -D "release $release" "$HOME"/rpmbuild/SPECS/fapolicy-analyzer.spec

mv /root/rpmbuild/RPMS/*/* /output
mv /root/rpmbuild/SRPMS/* /output
