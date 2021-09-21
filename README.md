File Access Policy Analyzer
===

Tools to assist with the configuration and maintenance of [fapolicyd](https://github.com/linux-application-whitelisting/fapolicyd).

## Python bindings

We write python bindings using [PyO3](https://github.com/PyO3/pyo3) and [setuptools_rust](https://setuptools-rust.readthedocs.io/en/latest/).

We use [pipenv](https://pipenv.pypa.io/en/latest/) for creating a sand-boxed development environment.  To install `pipenv` into your home directory:

```{shell}
pip3 install --user pipenv
```

To build and install the bindings run the following from the top level directory of this repository:

```{shell}
pipenv install --dev
pipenv shell
python3 setup.py [develop | install]
```

There may be some additional build-time requirements.  See [the development wiki page](https://github.com/ctc-oss/fapolicy-analyzer/wiki/Development) for more details.

## File Access Policy Analyzer User Interface

Run the fapolicy-analyzer UI:

```{shell}
python3 -m fapolicy-analyzer.ui
```

## Requirements

- Python 3.9
- Rust 1.52
- fapolicyd 1.0

### fapolicyd configuration
To generate rules that can be analyzed we require the following `syslog_format` configuration

`syslog_format = rule,dec,perm,uid,gid,pid,exe,:,path,ftype,trust`

## Developers

See the [Wiki](https://github.com/ctc-oss/fapolicy-analyzer/wiki) for more resources.
