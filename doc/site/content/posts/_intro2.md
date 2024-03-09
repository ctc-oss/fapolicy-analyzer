---
title: "Introduction - 2 - Installation"
date: 2024-03-09T17:02:50-05:00
---

## fapolicyd compatibility

Currently compatible with fapolicyd v1.0+. This will evolve in the future as minimum versions increase across

The fapolicy-analyzer tools

## Installation by supported platform

### RHEL 8 and RHEL 9 (stable)

The fapolicy-analyzer was first published to Fedora 8 with packages later added for RHEL 9.

```sh
todo;; install epel
dnf install fapolicy-analyzer
```

### Fedora (stable)

The fapolicy-analyzer was first published to Fedora 37. Since then releases have been maintained for each active Fedora
release, stopping when the release is EOL'd according to
the [Fedora release schedule](https://fedorapeople.org/groups/schedule/).

```sh
dnf install fapolicy-analyzer
```

### GitHub releases (stable and release candidates)

Stable and release candidate packages are available via
the [GitHub releases page](https://github.com/ctc-oss/fapolicy-analyzer/releases).

The releases are packaged as RPMs which can be downloaded and installed with the `rpm` command.

```shell
rpm -i fapolicy-analyzer.rpm
```

### Fedora Copr

The Copr repository contains the latest development builds which are built every time a commit is pushed to the master
branch.

This is the cutting edge functionality and is generally usable but makes no guarantees of stability. The commits are
validated by the automated testing implemented by the project, but there may have been no user testing for any given
commit.

The Copr repo also contains release builds prior to publishing to the Fedora repositories. These are used for testing
and will generally line up with the final release artifacts, but will not be exactly the same artifacts, as they are
rebuilt by Koji during the final release stage. The Copr release packages of the fapolicy-analyzer are generally
available from Copr a week before being available from Fedora.

The following installs and enables the Copr repository as a dnf source and installs the latest release package

```sh
dnf install dnf-plugins-core
dnf copr enable ctc-oss/fapolicy-analyzer
dnf install fapolicy-analyzer
```

### Copr pre-release builds

Pre-release packages of the Policy Analyzer for all targets are created using the latest commit to master.

Use the `dev` tag + the commit number from the `master` branch, for example

`dnf install fapolicy-analyzer-1.0.0~dev308`

will install the prerelease 1.0.0 version at the 308th commit on the master branch.

### Containerized build

Follow this method only if you have cloned the GitHub repository and have Podman or Docker installed

- `make fc-rpm` to build a Rawhide RPM
- `make el-rpm` to build a RHEL 8 RPM

After a successful build the container will copy the RPMs into the host `/tmp` directory.

### From a local development environment

Follow this method only if you have installed all required build tools

`make run`

This requires Pip + Pipenv + Python 3.9 or greater, and Rust 1.62.1 or greater.

Python and Rust dependencies will be installed during the build process.

todo;; add a section for installing development packages for testing releases
