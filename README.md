File Access Policy Analyzer
===

Tools to assist with the configuration and management of [fapolicyd](https://github.com/linux-application-whitelisting/fapolicyd).

[![Release](https://shields.io/github/v/release/ctc-oss/fapolicy-analyzer?color=blue&display_name=tag&sort=semver&label=Release)](https://github.com/ctc-oss/fapolicy-analyzer/releases)
![GitHub checks status](https://img.shields.io/github/checks-status/ctc-oss/fapolicy-analyzer/master?label=CI)
[![Copr build status](https://img.shields.io/badge/dynamic/json?color=B87333&label=Copr&query=builds.latest.state&url=https%3A%2F%2Fcopr.fedorainfracloud.org%2Fapi_3%2Fpackage%3Fownername%3Dctc-oss%26projectname%3Dfapolicy-analyzer%26packagename%3Dfapolicy-analyzer%26with_latest_build%3DTrue)](https://copr.fedorainfracloud.org/coprs/ctc-oss/fapolicy-analyzer/package/fapolicy-analyzer/)
![Coverity Scan](https://img.shields.io/coverity/scan/26261?label=Coverity)
![GitHub](https://img.shields.io/github/license/ctc-oss/fapolicy-analyzer?color=red&label=License)

## Install

- Using Copr

    ```text
    dnf install -y dnf-plugins-core
    dnf copr enable -y ctc-oss/fapolicy-analyzer
    dnf install -y fapolicy-analyzer
    ```
- Or RPM install from a GitHub release [:point_right:](https://github.com/ctc-oss/fapolicy-analyzer/releases/latest)
- Or `make fc-rpm` to build a Rawhide RPM from a Podman container
- Or `make el-rpm` to build a RHEL 8 RPM from a Podman container
- Or `make run` to run from a local development environment

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

- Start a [Discussion](https://github.com/ctc-oss/fapolicy-analyzer/discussions) with the team
- See the [Wiki](https://github.com/ctc-oss/fapolicy-analyzer/wiki) for more resources

## License

GPL v3
