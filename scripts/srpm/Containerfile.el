ARG image=registry.access.redhat.com/ubi8/ubi:8.6
FROM $image AS build-stage

RUN dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
RUN dnf install -y rpm-build dnf-plugins-core python3-pip nano

RUN useradd -u 10001 -g 0 -d /home/default default

USER 10001
RUN mkdir -p /home/default/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
WORKDIR /home/default/rpmbuild

COPY --chown=10001:0 scripts/srpm/fapolicy-analyzer.spec        SPECS/

USER root
RUN dnf -y builddep --skip-unavailable SPECS/fapolicy-analyzer.spec

USER 10001
WORKDIR /home/default/rpmbuild

COPY --chown=10001:0 fapolicy-analyzer.tar.gz SOURCES/
COPY --chown=10001:0 vendor-rs.tar.gz         SOURCES/
COPY --chown=10001:0 scripts/srpm/build.sh    ./build.sh

WORKDIR /home/default/rpmbuild

CMD ./build.sh
