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

To build and install the bindings run the following from the top level directory of this repository:

```{shell}
make shell
```

which under the hood is executing the following with the `develop` argument to setup.py:

```{shell}
pipenv install --dev
pipenv shell
python3 setup.py [develop | install]
```
### Using the make command driver

There are a number of make targets to kick-off common development tasks. Invoking make without a command-line target with list the higher level targets with a short summary:

```{shell}
$ make

  Usage: make [target]

       fapolicy-analyzer - High level common operation targets

     list     - Display common development targets
     shell    - Install deps, build bindings, start venv shell
     run      - Execute the fapolicy-analyzer
     test     - Execute all unit-tests
     lint     - Execute source code linting tools
     format   - Execute source code formatting
     check    - Perform pre-git push tests and formatting
     list-all - Display all targets

     Note: Options can be passed to fapolicy-analyzer by
           setting the OPTIONS environment variable, for example
             $ OPTIONS='-v' make run

     Note: Errors stop make, ignore them with the '-k' option:
             $ make -k [target]

```

Note: There may be some additional build-time requirements.  See [the development wiki page](https://github.com/ctc-oss/fapolicy-analyzer/wiki/Development) for more details.

## More Resources

## Getting Help
Feel free to ask a question or start a discussion in the [Discussion](https://github.com/ctc-oss/fapolicy-analyzer/discussions)


See the [Wiki](https://github.com/ctc-oss/fapolicy-analyzer/wiki) for more resources.

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

## Reporting an issue

Before submitting an issue:

-   A clear title
-   Provide as detailed a description as possible and ideally the steps to
    duplicate the issue.
