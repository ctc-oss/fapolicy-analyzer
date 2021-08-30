File Access Policy Analyzer
===

Tools to assist with the configuration and maintenance of [fapolicyd](https://github.com/linux-application-whitelisting/fapolicyd).

## Python bindings

We write python bindings using [PyO3](https://github.com/PyO3/pyo3) and [setuptools_rust](https://setuptools-rust.readthedocs.io/en/latest/).

To build and install the bindings run the following from the [python](python) directory:

```
pipenv install --dev
pipenv shell
python setup.py [develop | install]
python examples/validate_install.py
```

## Requirements

- Python 3
- Rust 1.52
- fapolicyd 1.0

### fapolicyd configuration
To generate rules that can be analyzed we require the following `syslog_format` cnofiguration

`syslog_format = rule,dec,perm,uid,gid,pid,exe,:,path,ftype,trust`

## Developers

See the [Wiki](https://github.com/ctc-oss/fapolicy-analyzer/wiki) for more resources.
