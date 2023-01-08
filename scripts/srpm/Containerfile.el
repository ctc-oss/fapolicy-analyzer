ARG image=rockylinux:8.6
FROM $image AS build-stage

RUN dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
RUN dnf install -y rpm-build rpmdevtools dnf-plugins-core python3-pip nano

RUN useradd -u 10001 -g 0 -d /home/default default

USER 10001
RUN mkdir -p /tmp/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
WORKDIR /tmp/rpmbuild

COPY --chown=10001:0 scripts/srpm/fapolicy-analyzer.spec SPECS/

USER root
RUN dnf -y builddep SPECS/fapolicy-analyzer.spec

USER 10001
WORKDIR /tmp/rpmbuild

RUN spectool -gf -C SOURCES/ SPECS/fapolicy-analyzer.spec || true

COPY --chown=10001:0 fapolicy-analyzer.tar.gz SOURCES/
COPY --chown=10001:0 vendor-rs.tar.gz         SOURCES/
COPY --chown=10001:0 scripts/srpm/build.sh    ./build.sh

WORKDIR /tmp/rpmbuild/SOURCES
RUN dist=$(rpm --eval "%{?dist}") \
 && mv vendor-rs.tar.gz vendor-rs${dist}.tar.gz

WORKDIR /tmp/rpmbuild

ENTRYPOINT ["/tmp/rpmbuild/build.sh"]
