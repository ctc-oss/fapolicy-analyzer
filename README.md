File Access Policy Analyzer
===

Tools to assist with the configuration and management of [fapolicyd](https://github.com/linux-application-whitelisting/fapolicyd).

[![Fedora package](https://img.shields.io/fedora/v/fapolicy-analyzer?logo=fedora&label=Fedora)](https://packages.fedoraproject.org/pkgs/fapolicy-analyzer/fapolicy-analyzer/)
[![GitHub release](https://shields.io/github/v/release/ctc-oss/fapolicy-analyzer?color=blue&display_name=tag&sort=semver&label=GitHub)](https://github.com/ctc-oss/fapolicy-analyzer/releases/latest)
![GitHub CI](https://badgen.net/github/checks/ctc-oss/fapolicy-analyzer?label=CI)
[![Copr build status](https://img.shields.io/badge/dynamic/json?color=B87333&label=Copr&query=builds.latest.state&url=https%3A%2F%2Fcopr.fedorainfracloud.org%2Fapi_3%2Fpackage%3Fownername%3Dctc-oss%26projectname%3Dfapolicy-analyzer%26packagename%3Dfapolicy-analyzer%26with_latest_build%3DTrue)](https://copr.fedorainfracloud.org/coprs/ctc-oss/fapolicy-analyzer/)
[![Coverity Scan](https://img.shields.io/coverity/scan/26261?label=Coverity)](https://scan.coverity.com/projects/ctc-oss-fapolicy-analyzer)
![GitHub](https://img.shields.io/github/license/ctc-oss/fapolicy-analyzer?color=red&label=License)

## Install

You can install the Policy Analyzer in one of the following ways

<details>

  <summary>Using Official Fedora Packages</summary>

This installation method is currently available for Fedora 37 and greater, including Rawhide.

Official EPEL releases are coming, but are not yet available.  See the Copr releases for EPEL 8.

```sh
dnf install fapolicy-analyzer
```

</details>

<details>

  <summary>From GitHub releases</summary>

![GitHub download counter](https://img.shields.io/github/downloads/ctc-oss/fapolicy-analyzer/total?color=success&logo=github)

You can install the Policy Analyzer through the installers available in the [latest release](https://github.com/ctc-oss/fapolicy-analyzer/releases). <br>
Choose an RPM from the latest Fedora stable, Rawhide, and EPEL builds. <br>

</details>

<details>

  <summary>Using Fedora Copr</summary>

Follow this method to install EPEL 8 and prerelease packages.

### Add Copr repository

Install the ctc-oss repo with

```sh
dnf install dnf-plugins-core
dnf copr enable ctc-oss/fapolicy-analyzer
```

### Copr EPEL builds

EPEL releases of the Policy Analyzer are available from Copr and can be installed with the normal process

`dnf install fapolicy-analyzer`

### Copr pre-release builds

Pre-release packages of the Policy Analyzer for all targets are created using the latest commit to master.

Use the `dev` tag + the commit number from the `master` branch, for example

`dnf install fapolicy-analyzer-1.0.0~dev308`

will install the prerelease 1.0.0 version at the 308th commit on the master branch.

</details>

<details>

  <summary>From a containerized build environment</summary>

Follow this method only if you have cloned the GitHub repository and have Podman installed

- `make fc-rpm` to build a Rawhide RPM
- `make el-rpm` to build a RHEL 8 RPM

After a successful build the container will copy the RPMs into the host `/tmp` directory.

</details>


<details>

  <summary>From a local development environment</summary>

Follow this method only if you have installed all required build tools

`make run`

This requires Pip + Pipenv + Python 3.6 or greater, and Rust 1.62.1 or greater.

Python and Rust dependencies will be installed during the build process.

</details>

## fapolicyd

We aim to be compatible back to v1.0, but newer versions will likely work best.

To analyze from syslog we require the following `syslog_format` in fapolicyd.conf

```
syslog_format = rule,dec,perm,uid,gid,pid,exe,:,path,ftype,trust
```

## Getting Help

- Start a [Discussion](https://github.com/ctc-oss/fapolicy-analyzer/discussions)
- Open an [Issue](https://github.com/ctc-oss/fapolicy-analyzer/issues)
- See the [Wiki](https://github.com/ctc-oss/fapolicy-analyzer/wiki)

## License

GPL v3
