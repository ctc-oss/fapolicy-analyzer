File Access Policy Analyzer
===

Tools to assist with the configuration and management of [fapolicyd](https://github.com/linux-application-whitelisting/fapolicyd).

[![Fedora package](https://img.shields.io/fedora/v/fapolicy-analyzer?logo=fedora&label=Fedora)](https://src.fedoraproject.org/rpms/fapolicy-analyzer)
[![GitHub release](https://shields.io/github/v/release/ctc-oss/fapolicy-analyzer?color=blue&display_name=tag&sort=semver&label=GitHub)](https://github.com/ctc-oss/fapolicy-analyzer/releases)
[![Copr build status](https://img.shields.io/badge/dynamic/json?color=B87333&label=Copr&query=builds.latest.state&url=https%3A%2F%2Fcopr.fedorainfracloud.org%2Fapi_3%2Fpackage%3Fownername%3Dctc-oss%26projectname%3Dfapolicy-analyzer%26packagename%3Dfapolicy-analyzer%26with_latest_build%3DTrue)](https://copr.fedorainfracloud.org/coprs/ctc-oss/fapolicy-analyzer/package/fapolicy-analyzer/)
[![Coverity Scan](https://img.shields.io/coverity/scan/26261?label=Coverity)](https://scan.coverity.com/projects/ctc-oss-fapolicy-analyzer)
![GitHub checks status](https://img.shields.io/github/checks-status/ctc-oss/fapolicy-analyzer/master?label=CI)
![GitHub](https://img.shields.io/github/license/ctc-oss/fapolicy-analyzer?color=red&label=License)

## Install

You can install the Policy Analyzer in one of the following ways

<details>

  <summary>Using Official Fedora Packages</summary>

This installation method is currently available for Fedora 37 and greater, including Rawhide.

EPEL releases are planned but are not yet available.

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

Follow this method only if you want prerelease test builds. If so, the package can be installed with

```sh
dnf install -y dnf-plugins-core
dnf copr enable -y ctc-oss/fapolicy-analyzer
dnf install -y fapolicy-analyzer
```

</details>

<details>

  <summary>From a containerized build environment</summary>

Follow this method only if you have cloned the repository and have Podman installed

- `make fc-rpm` to build a Rawhide RPM
- `make el-rpm` to build a RHEL 8 RPM

When successful the container will copy the RPMs into the host `/tmp` directory.

</details>


<details>

  <summary>From a local development environment</summary>

Follow this method only if you want to install the full suite of development and build tools

`make run`

This requires Pip + Pipenv + Python 3.6 or greater, and Rust 1.58.1 or greater.

Dependencies of each will be automatically installed during the build process.

</details>

## Requirements

- Python 3.6
- Rust 1.58.1
- fapolicyd 1.x

### fapolicyd configuration

To analyze from syslog we require the following `syslog_format` in fapolicyd.conf
```
syslog_format = rule,dec,perm,uid,gid,pid,exe,:,path,ftype,trust
```

## Getting Help

- See the [Wiki](https://github.com/ctc-oss/fapolicy-analyzer/wiki)
- Start a [Discussion](https://github.com/ctc-oss/fapolicy-analyzer/discussions)
- Create an [Issue](https://github.com/ctc-oss/fapolicy-analyzer/issues)

## License

GPL v3
