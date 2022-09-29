File Access Policy Analyzer SRPM build
===

[![Copr build status](https://copr.fedorainfracloud.org/coprs/ctc-oss/fapolicy-analyzer/package/fapolicy-analyzer/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/ctc-oss/fapolicy-analyzer/package/fapolicy-analyzer/)

## From Copr

```text
dnf install -y dnf-plugins-core
dnf copr enable -y ctc-oss/fapolicy-analyzer
dnf install -y fapolicy-analyzer
```

## From dev env

Build from Rawhide container with Podman

```text
make -f .copr/Makefile vendor
podman build -t fapolicy-analyzer:rawhide -f scripts/srpm/Containerfile.fc .
podman run --rm -it --network=none fapolicy-analyzer:rawhide
```

or from a RHEL container

```text
make -f .copr/Makefile vendor
podman build -t fapolicy-analyzer:el -f scripts/srpm/Containerfile.el .
podman run --rm -it --network=none fapolicy-analyzer:el
```

Both examples produce a disconnected build using an unprivileged user.

## references

- https://developer.fedoraproject.org/deployment/rpm/about.html
