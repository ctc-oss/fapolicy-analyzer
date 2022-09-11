File Access Policy Analyzer SRPM build
===

[![Copr build status](https://copr.fedorainfracloud.org/coprs/jwass3/fapolicy-analyzer/package/fapolicy-analyzer/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/jwass3/fapolicy-analyzer/package/fapolicy-analyzer/)

## From Copr

From Rawhide Vagrant machine

```text
dnf install -y dnf-plugins-core
dnf copr enable -y jwass3/fapolicy-analyzer
dnf install -y fapolicy-analyzer
```


## From dev env

From Rawhide container with Podman

```text
make -f .copr/Makefile vendor
podman build --security-opt seccomp=unconfined -t fapolicy-analyzer:rawhide -f scripts/srpm/Containerfile .
podman run --rm -it fapolicy-analyzer:rawhide
```
