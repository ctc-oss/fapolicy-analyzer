# Contributing Guide

Thank you for your efforts to improve the fapolicy-analyzer project. This guide
will help you regarding various aspects like submitting issues, contributing a
feature, etc.

## Developers

See the [Wiki](https://github.com/ctc-oss/fapolicy-analyzer/wiki) for more resources.

---

## Before Submitting a Pull Request

**Before submitting your pull request**

-   Clone the repository
-   Create a branch from `master`
-   Run `make shell` in the repository root
-   Change necessary code for bug fix, a new feature
-   Check linting and format it

```bash
make lint
make format
```

-   Make sure all  unit-tests pass and that there is greater than 90% converage.

```bash
make test
```

## Reporting an issue

Before submitting an issue:

-   A clear title
-   Provide as detailed a description as possible and ideally the steps to
    duplicate the issue.
