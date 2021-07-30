ARG platform=fedora:32
FROM ${platform} AS build-stage

RUN dnf install -y rpm-build rpmdevtools dnf-plugins-core python3-jinja2-cli \
 && dnf clean all

RUN mkdir -p /root/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
COPY fapolicy-analyzer.spec.j2 ./

ARG fedora_ver=
ARG git_commit=
ARG rpm_version=
ARG rpm_release=

# Rather than passing the variables directly to rpmbuild, burn the values
# into the spec file with jinja so the spec in the src.rpm works standalone.
RUN jinja2 \
        -D fedora_ver=${fedora_ver} \
        -D git_commit=${git_commit} \
        -D rpm_version=${rpm_version} \
        -D rpm_release=${rpm_release} \
        fapolicy-analyzer.spec.j2 > /root/rpmbuild/SPECS/fapolicy-analyzer.spec

RUN cd /root/rpmbuild/SOURCES                    \
 && spectool -gf ../SPECS/fapolicy-analyzer.spec \
 && cd /root/rpmbuild/SPECS                      \
 && dnf builddep fapolicy-analyzer.spec -y       \
 && rpmbuild -ba fapolicy-analyzer.spec

FROM scratch AS export-stage
COPY --from=build-stage /root/rpmbuild/SRPMS/*.src.rpm /
COPY --from=build-stage /root/rpmbuild/RPMS/x86_64/*.rpm /
