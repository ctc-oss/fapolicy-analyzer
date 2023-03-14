<div align="center">
  <h1><samp>File Access Policy Analyzer</samp></h1>


<p>
<a href="https://packages.fedoraproject.org/pkgs/fapolicy-analyzer/fapolicy-analyzer/"><img src="https://img.shields.io/fedora/v/fapolicy-analyzer?logo=fedora&label=Fedora&color=3c6eb4"></a>
<a href="https://github.com/ctc-oss/fapolicy-analyzer/releases"><img src="https://img.shields.io/github/v/release/ctc-oss/fapolicy-analyzer?color=4078c0&include_prereleases&label=GitHub&logo=github"></a>
<a href="https://copr.fedorainfracloud.org/coprs/ctc-oss/fapolicy-analyzer/"><img src="https://img.shields.io/badge/dynamic/json?color=B87333&logo=fedora&label=Copr&query=builds.latest.state&url=https%3A%2F%2Fcopr.fedorainfracloud.org%2Fapi_3%2Fpackage%3Fownername%3Dctc-oss%26projectname%3Dfapolicy-analyzer%26packagename%3Dfapolicy-analyzer%26with_latest_build%3DTrue"></a>
<img src="https://badgen.net/github/checks/ctc-oss/fapolicy-analyzer?label=CI">
<a href="https://scan.coverity.com/projects/ctc-oss-fapolicy-analyzer"><img src="https://img.shields.io/coverity/scan/26261?label=Coverity"></a>
<img src="https://img.shields.io/github/license/ctc-oss/fapolicy-analyzer?color=3c6eb4&label=License">
</p>

<p>
<strong>Tools to assist with the configuration and management of <a href="https://github.com/linux-application-whitelisting/fapolicyd">fapolicyd</a></strong>
</p>

</div>

## Features

1. Edit rules with validation and syntax highlighting
2. Diff trust between fapolicyd trust db and disk
3. Analyze fapolicyd logs and fix trust discrepancies
4. Profile application disk access in fapolicy permissive mode

See the [**User Guide**][1] for details.

## Installation

You can install the Policy Analyzer in one of the following ways

<details>

  <summary>From Fedora Packages</summary>

This installation method is currently available for Fedora EPEL 8, and Fedora 37 or later, including Rawhide.

```sh
dnf install fapolicy-analyzer
```

</details>

<details>

  <summary>From GitHub releases</summary>

[![GitHub latest release](https://shields.io/github/v/release/ctc-oss/fapolicy-analyzer?color=3c6eb4&display_name=tag&sort=semver&label=Stable&logo=github)](https://github.com/ctc-oss/fapolicy-analyzer/releases/latest)
[![GitHub Latest pre-release)](https://img.shields.io/github/v/release/ctc-oss/fapolicy-analyzer?color=3c6eb4&include_prereleases&label=Beta&logo=github)](https://github.com/ctc-oss/fapolicy-analyzer/releases)
![GitHub downloads](https://img.shields.io/github/downloads/ctc-oss/fapolicy-analyzer/total?color=3c6eb4&logo=github)

You can install the Policy Analyzer through the installers available in the [latest release](https://github.com/ctc-oss/fapolicy-analyzer/releases). <br>
Choose an RPM from the latest Fedora stable, Rawhide, and EPEL builds. <br>

</details>

<details>

  <summary>From Fedora Copr</summary>

The Copr repository contains the latest development builds and release builds prior to publishing to the Fedora repositories.

Follow this method to install a prerelease package.

### Add Copr repository

Install the ctc-oss repo with

```sh
dnf install dnf-plugins-core
dnf copr enable ctc-oss/fapolicy-analyzer
```

### Copr Release builds

Releases packages of the Policy Analyzer are generally available from Copr a week before being available from Fedora.

The Policy Analyzer can be installed from the ctc-oss repository with the normal process

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

v1.0+ is supported.

Issues labeled [![fapolicyd-badge](https://img.shields.io/github/labels/ctc-oss/fapolicy-analyzer/fapolicyd%20feature?style=flat)][3] indicate the level of support.

### fapolicyd.conf

To analyze from syslog we require the following `syslog_format`:

```
syslog_format = rule,dec,perm,uid,gid,pid,exe,:,path,ftype,trust
```

## Getting Help

- See the [Known Issues](https://github.com/ctc-oss/fapolicy-analyzer/wiki/Known-Issues)
- Start a [Discussion](https://github.com/ctc-oss/fapolicy-analyzer/discussions)
- Create a new [Issue](https://github.com/ctc-oss/fapolicy-analyzer/issues)

## License

GPL v3

[1]: https://github.com/ctc-oss/fapolicy-analyzer/wiki/User-Guide
[2]: https://github.com/ctc-oss/fapolicy-analyzer/labels/fapolicyd%20feature
[3]: https://github.com/linux-application-whitelisting/fapolicyd/blob/main/ChangeLog
