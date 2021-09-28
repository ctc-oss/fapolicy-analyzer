ARG platform=fedora:34
FROM ${platform} AS build-stage

# On RHEL, enable the Rocky AppStream repo for a few packages not in ubi.
RUN grep -e "^Red Hat Enterprise Linux" /etc/redhat-release \
 && RELEASE=$(grep -oE "[0-9]+\.[0-9]+" /etc/redhat-release) \
 && printf "[rocky-$RELEASE-appstream]\nname=Rocky Linux $RELEASE - AppStream\nbaseurl=http://dl.rockylinux.org/pub/rocky/$RELEASE/AppStream/x86_64/os/\ngpgcheck=1\nenabled=1\ngpgkey=https://git.rockylinux.org/label/rocky-repos/-/raw/r8/SOURCES/RPM-GPG-KEY-rockyofficial\nincludepkgs=rpmdevtools,dbus-devel\n" > /etc/yum.repos.d/Rocky-"$RELEASE"-AppStream.repo \
 || true

# Install base toolchain; for tools not packaged in el8, just use pip always.
RUN dnf install -y rpm-build rpmdevtools dnf-plugins-core python3-pip \
 && pip3 install --no-input jinja2-cli \
 && dnf clean all

RUN mkdir -p /root/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
COPY fapolicy-analyzer.spec.j2 ./

ARG pyrpm=python3
ARG git_commit=
ARG rpm_version=
ARG rpm_release=

# Rather than passing the variables directly to rpmbuild, burn the values
# into the spec file with jinja so the spec in the src.rpm works standalone.
RUN jinja2 \
        -D pyrpm=${pyrpm} \
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
