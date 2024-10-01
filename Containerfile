ARG image=registry.fedoraproject.org/fedora:latest
FROM $image AS fedorabuild
ARG version
ARG spec=fapolicy-analyzer.spec

# rpmbuild tools could be installed in the el stage
# but caching them here ends up saving time on rebuilds
RUN dnf install -y mock rpm-build rpmdevtools

RUN useradd -u 10001 -g 0 -d /home/default default

USER 10001
RUN mkdir -p /tmp/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
WORKDIR /tmp/rpmbuild

COPY --chown=10001:0 $spec SPECS/fapolicy-analyzer.spec

USER root
RUN dnf -y builddep SPECS/fapolicy-analyzer.spec

USER 10001

COPY --chown=10001:0 fapolicy-analyzer-$version.tar.gz SOURCES/
COPY --chown=10001:0 vendor-docs-$version.tar.gz       SOURCES/
COPY --chown=10001:0 scripts/srpm/build.sh             .

USER root

ENTRYPOINT ["/tmp/rpmbuild/build.sh"]

FROM fedorabuild as elbuild
ARG version

USER 10001

RUN spectool --list-files SPECS/fapolicy-analyzer.spec | grep pythonhosted | cut -d' ' -f2 | xargs -I{} curl -sLO --output-dir SOURCES {}

COPY --chown=10001:0 vendor-rs-$version.tar.gz         SOURCES/

USER root
