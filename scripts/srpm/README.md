File Access Policy Analyzer SRPM build
===

From the root project

```text
make -f .copr/Makefile vendor
podman build --security-opt seccomp=unconfined -t fapolicy-analyzer:rawhide -f scripts/srpm/Containerfile .
podman run --rm -it fapolicy-analyzer:rawhide
```
