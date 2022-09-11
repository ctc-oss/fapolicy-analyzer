File Access Policy Analyzer SRPM build
===

[![Copr build status](https://copr.fedorainfracloud.org/coprs/jwass3/fapolicy-analyzer/package/fapolicy-analyzer/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/jwass3/fapolicy-analyzer/package/fapolicy-analyzer/)

From the root project

```text
make -f .copr/Makefile vendor
podman build --security-opt seccomp=unconfined -t fapolicy-analyzer:rawhide -f scripts/srpm/Containerfile .
podman run --rm -it fapolicy-analyzer:rawhide
```
