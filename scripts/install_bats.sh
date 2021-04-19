#!/usr/bin/env bash

mkdir /tmp/bats
cd /tmp/bats || exit 1
curl -Lo bats.tar.gz https://github.com/bats-core/bats-core/archive/refs/tags/v1.3.0.tar.gz
curl -Lo bats-assert.tar.gz https://github.com/bats-core/bats-assert/archive/refs/tags/v2.0.0.tar.gz
curl -Lo bats-support.tar.gz https://github.com/bats-core/bats-support/archive/refs/tags/v0.3.0.tar.gz
for gz in *.gz; do tar xvzf $gz; done

cd bats-core-* || exit 1
./install.sh "$HOME/.local"
cd -

mkdir -p "$HOME/.local/share/bats/assert"
mkdir -p "$HOME/.local/share/bats/support"

cp -r bats-assert-*/* "$HOME/.local/share/bats/assert"
cp -r bats-support-*/* "$HOME/.local/share/bats/support"

rm -rf /tmp/bats*
