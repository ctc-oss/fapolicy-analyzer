fapolicy analyzer rpm
===

## summary

1. build a wheel
2. use the wheel as the rpm source
3. install the wheel during the rpm build

### build the builder image

From the root of the project

`docker build -t rpmbuilder -f scripts/rpm/Dockerfile .`

### build the rpm in the builder container

`docker run --rm -it -v /tmp:/output rpmbuilder:latest`

RPMs will end up in `/tmp` on the host machine.

### test installing rpm in a container

`docker run --rm -it -v /tmp:/rpms fedora:32 dnf install -y /rpms/fapolicy-analyzer-*.rpm`
