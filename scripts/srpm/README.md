File Access Policy Analyzer SRPM build
===

The Containerfile and spec file in this directory contain WIP RHEL support.

The root directory version should be considered the stable version.

To build from the RHEL container 

```text
make -f .copr/Makefile vendor
podman build -t fapolicy-analyzer:el -f scripts/srpm/Containerfile.el .
podman run --rm -it --network=none fapolicy-analyzer:el
```

Or from the Makefile in root use the `el-rpm` target.

Both methods produce a disconnected build using an unprivileged user.

## references

- https://developer.fedoraproject.org/deployment/rpm/about.html
