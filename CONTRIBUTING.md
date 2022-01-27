# Contributing Guide

Thank you for your efforts to improve the fapolicy-analyzer project. This guide
will help you regarding various aspects like submitting issues, contributing a
feature, etc.

## Developers

### Python bindings

We write python bindings using [PyO3](https://github.com/PyO3/pyo3) and [setuptools_rust](https://setuptools-rust.readthedocs.io/en/latest/).

We use [pipenv](https://pipenv.pypa.io/en/latest/) for creating a sand-boxed development environment.  To install `pipenv` into your home directory:

```{shell}
pip3 install --user pipenv
```

To build and install the bindings, and to start the virtual development environment, run the following from the top level directory of this repository:

```{shell}
make shell
```

Note: There may be some additional build-time requirements.  See [the development wiki page](https://github.com/ctc-oss/fapolicy-analyzer/wiki/Development) for more details.

### Before Submitting a Pull Request

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

### Getting Help
Feel free to ask a question or start a discussion in the [Discussion](https://github.com/ctc-oss/fapolicy-analyzer/discussions) section of this project.

### More Resources

As mentioned above, there is a dedicated [Development](https://github.com/ctc-oss/fapolicy-analyzer/wiki/Development) section on the wiki.

See the [Wiki](https://github.com/ctc-oss/fapolicy-analyzer/wiki) for more general resources.

The [fapolicyd](https://github.com/linux-application-whitelisting/fapolicyd) project.

## Reporting an issue

Before submitting an issue:

-   A clear title
-   Provide as detailed a description as possible and ideally the steps to
    duplicate the issue.
