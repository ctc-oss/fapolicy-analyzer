---
title: "Introduction - 2 - Installation"
date: 2024-03-09T17:02:50-05:00
---

## fapolicyd compatibility

Currently compatible with fapolicyd v1.0+.
The [fapolicyd-feature](https://github.com/ctc-oss/fapolicy-analyzer/labels/fapolicyd-feature) label in the issue
tracker contains specific compatibility issues.

## Installation by supported platform

### RHEL 8 and RHEL 9 (stable)

The fapolicy-analyzer was first published to Fedora 8 with packages later added for RHEL 9.

```sh
dnf install epel-release
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

## Configuring fapolicy-analyzer

The packaged fapolicy-analyzer configuration should be suitable for most installations. However there are some
configuration flags that can be set to control low level behavior.

### Common issues

The most common issue when starting the fapolicy-analyzer the first time will occur on a system where fapolicyd has not
yet been run. This is due to the initialization that fapolicyd performs on startup rather than on install. The
fapolicy-analyzer may display a dialog like this:

![failed-to-init](https://github.com/ctc-oss/fapolicy-analyzer/wiki/site/failed-to-start.png)

On a standard install this is indicating that disk location like the trust database have not yet been initialized. In a
future release the fapolicy-analyzer will provide specific error indications rather than the list of possible issues.
There may also be a point in the future where the fapolicy-analyzer will initialize these locations rather than relying
on fapolicyd to run first.

### config.toml

The fapolicy-analyzer configuration can be tuned for development or non-standard installations. The default
configuration looks like

```toml
[system]
rules_file_path = '/etc/fapolicyd/rules.d'
trust_lmdb_path = '/var/lib/fapolicyd'
system_trust_path = '/var/lib/rpm'
trust_dir_path = '/etc/fapolicyd/trust.d'
trust_file_path = '/etc/fapolicyd/fapolicyd.trust'
syslog_file_path = '/var/log/messages'
config_file_path = '/etc/fapolicyd/fapolicyd.conf'

[application]
data_dir = '/home/me/.local/share/fapolicy-analyzer'
```

The paths in this file will vary depending on deployment target. On Fedora systems the standard filesystem paths are
used for state and configuration (etc, var) while on development deployments
the [XDG file paths](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) are used for
portability and convenience.

---

In the next post in this series we will step through rule editing and deployment with the assistance of the syntax
checker, linter, and in-line d-directory editing.

Additional information can be found in
the [fapolicy-analyzer user guide](https://github.com/ctc-oss/fapolicy-analyzer/wiki/User-Guide) which is available on
the GitHub Wiki and is also packaged in the RPM packages.
