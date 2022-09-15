ARG image=registry.access.redhat.com/ubi8/ubi:8.6
FROM $image AS build-stage

ARG USERNAME
ARG PASSWORD

RUN rm /etc/rhsm-host

# appears we must activate for appstream with dbus-devel
#RUN subscription-manager register --username $USERNAME --password $PASSWORD \
# && subscription-manager attach --servicelevel=standard

RUN dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
RUN dnf install -y rpm-build dnf-plugins-core python3-pip nano

WORKDIR /root/rpmbuild

RUN mkdir -p {BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
COPY scripts/srpm/fapolicy-analyzer.spec        SPECS/

RUN dnf -y builddep --skip-unavailable SPECS/fapolicy-analyzer.spec

COPY fapolicy-analyzer.tar.gz SOURCES/
COPY vendor-rs.tar.gz         SOURCES/
COPY vendor-py.tar.gz         SOURCES/
COPY scripts/srpm/build.sh    ./build.sh

WORKDIR /root/rpmbuild

CMD ./build.sh
