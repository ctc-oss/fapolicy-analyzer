ARG image=registry.fedoraproject.org/fedora:latest
FROM $image AS build-stage
ARG version

RUN dnf install -y mock

RUN useradd -u 10001 -g 0 -d /home/default default

USER 10001
RUN mkdir -p /tmp/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
WORKDIR /tmp/rpmbuild

COPY --chown=10001:0 fapolicy-analyzer.spec SPECS/

USER root
RUN dnf -y builddep SPECS/fapolicy-analyzer.spec

USER 10001

COPY --chown=10001:0 fapolicy-analyzer-$version.tar.gz SOURCES/
COPY --chown=10001:0 vendor-docs-$version.tar.gz       SOURCES/
COPY --chown=10001:0 scripts/srpm/build.sh    ./build.sh

USER root

ENTRYPOINT ["/tmp/rpmbuild/build.sh"]
