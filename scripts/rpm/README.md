fapolicy analyzer rpm
===

Build an RPM that includes the Rust bindings and the Python dist.  The standard tools for building Python RPMs or Rust RPMs didn't play well with our layout. 
So what we have is a two stage process of (1) building a bdist wheel and (2) using that wheel to build the RPM. The source RPM includes the wheel as the only source file.

### how we package

1. build a wheel
2. use the wheel as the rpm source
3. install the wheel in the rpm build
4. capture the python site-install files

### build the builder image

From the root of the project

`docker build -t rpmbuilder -f scripts/rpm/Dockerfile .`

### build the rpm in the builder container

`docker run --rm -it -v /tmp:/output rpmbuilder:latest`

RPMs will end up in `/tmp` on the host machine.

### test installing rpm in a container

`docker run --rm -it -v /tmp:/rpms fedora:32 dnf install -y /rpms/fapolicy-analyzer-*.rpm`
