#!/usr/bin/env bash

readonly rules=$1
readonly config=fapolicyd.conf
readonly allowdir=/tmp/allow
readonly denydir=/tmp/deny

mkdir $allowdir $denydir
cp /bin/ls $allowdir
cp /bin/ls $denydir

readonly cname=testing-fapolicyd-runsh

sudo podman run -d --name $cname --rm -it \
              --privileged \
              -v "$PWD/$rules:/etc/fapolicyd/fapolicyd.rules" \
              -v "$PWD/$config:/etc/fapolicyd/fapolicyd.conf" \
              -v "$allowdir:/allow" \
              -v "$denydir:/deny"  \
              ctcoss/fapolicyd

sudo podman exec -it $cname groupadd -g 12345 test
sudo podman exec -it $cname useradd -g 12345 -u 10001 tester

sudo podman exec -u 10001 -it $cname bash

sudo podman exec -it $cname journalctl -u fapolicyd

sudo podman kill $cname

echo "done"
