#!/usr/bin/env bash

readonly version=0.0.4

mkdir -p "$HOME"/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

python setup.py bdist_wheel

cp dist/fapolicy_analyzer-*.whl "$HOME"/rpmbuild/SOURCES

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cp "$SCRIPT_DIR/fapolicy-analyzer.spec" "$HOME"/rpmbuild/SPECS

rpmbuild -ba --define "version $version" "$HOME"/rpmbuild/SPECS/fapolicy-analyzer.spec

# Wrote: /root/rpmbuild/SRPMS/fapolicy-analyzer-0.0.4-1.src.rpm
# Wrote: /root/rpmbuild/RPMS/x86_64/fapolicy-analyzer-0.0.4-1.x86_64.rpm

mv /root/rpmbuild/RPMS/*/* /output
mv /root/rpmbuild/SRPMS/* /output
