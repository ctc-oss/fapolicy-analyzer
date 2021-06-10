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

### test the rpm in a container
`todo`

### installing the rpm

`dnf install -y fapolicy-analyzer-0.0.4-1.x86_64.rpm`
