fapolicy analyzer rpm
===

### how we package

Args:

fedora_ver
: Numeric fedora release
: Used to choose the installation method for python setuptools rust: package for fedora 34+ or pip for earlier.

git_commit
: Git tag or commit to package
: Used to contruct the URL for the package archive.

rpm_version
: Package version

rpm_release
: Package release

Build steps:

1. Install basic rpmbuild toolchain:
   - rpm-build
   - rpmdevtools: provides spectool to download source archive
   - dnf-plugins-core: provides builddep to download dependencies
   - python3-jinja2-cli: create standalone spec file from template

2. Generate the standalone spec file from the template and args
   - FEDORA_VER: read VERSION_ID from /etc/os-release
   - GIT_COMMIT: exact git tag or git commit hash
   - RPM_VERSION: from git-rpm-version
   - RPM_RELEASE: from git-rpm-version

3. Download package source with spectool

4. Install package build dependencies with builddep

5. Build the package with rpmbuild

### build the rpm in docker

`./build.sh /tmp/rpms 33 34`

RPMs for Fedora 33 and 34 will end up in `/tmp/rpms` on the host machine.

### test installing rpm in a container

`docker run --rm -it -v /tmp/rpms:/rpms fedora:34 sh -c 'dnf install -y /rpms/fapolicy-analyzer-*.fc34.x86_64.rpm'`

### rebuild from src.rpm in a container

`docker run --rm -it -v /tmp/rpms:/rpms fedora:34 sh -c 'dnf install -y rpm-build dnf-plugins-core ; dnf builddep -y /rpms/fapolicy-analyzer-*.fc34.src.rpm ; rpmbuild --rebuild /rpms/fapolicy-analyzer-*.fc34.src.rpm ; ls -lR /root/rpmbuild/RPMS'`
