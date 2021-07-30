#!/bin/sh

if [ $# -lt 2 ]
then
       echo "Usage: `basename $0` out_directory fedora_tag1 [ fedora_tag2 ... ]"
       exit 1
fi

_output="${1}"
shift

for F in $@
do
       DOCKER_BUILDKIT=1 docker build \
               -o "${_output}" \
               --build-arg platform=fedora:"$F" \
               --build-arg fedora_ver="$F" \
               --build-arg git_commit="$(git describe --match "v*" --abbrev=0 --candidates=0 || git rev-parse --verify HEAD)" \
               --build-arg rpm_version="$(git describe --always --match "v*" | sed -e 's/^v//' -e 's/-rc[0-9]*//' -e 's/-[0-9]\{1,\}-g[0-9a-f]\{1,\}//' -e 's/-/\./g')" \
               --build-arg rpm_release="0$(git describe --always --match "v*" | sed -e 's/[^-]\{1,\}//' -e 's/-/./g')" \
               --build-arg http_proxy="$http_proxy" \
               --build-arg https_proxy="$https_proxy" \
               .
done
