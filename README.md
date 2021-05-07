File Access Policy Analyzer
===

Tools to assist with the configuration and maintenance of [fapolicyd](https://github.com/linux-application-whitelisting/fapolicyd).

### Python bindings

We write python bindings using [PyO3](https://github.com/PyO3/pyo3) and [setuptools_rust](https://setuptools-rust.readthedocs.io/en/latest/).

To build and install the bindings run the following from the [python](python) directory:

```
pipenv install --dev
pipenv shell
python setup.py [develop | install]
python examples/validate_install.py
```

### Integration tests

We write integration tests using [Bats](https://bats-core.readthedocs.io/en/latest/index.html) and [Podman](https://podman.io/).  The integration tests can run locally or in Travis CI.

A Bats test that validates changing the trust database looks like:

```bash
@test "trust: add" {
  # initially denied :thumbs_down:
  run in_container /deny/simple.sh
  assert_output --partial "permission denied"

  # add a trust entry for the script
  run in_container python3 examples/add_trust.py /deny/simple.sh
  assert_output --partial "applying"
  assert_output --partial "signaling"

  # check the fapolicyd trust db for the new entry
  run in_container python3 examples/show_ancillary.py
  assert_output --partial "/deny/simple.sh"

  # now its runs :thumbs_up:
  run in_container /deny/simple.sh
  assert_output "OK"
}
```

See the [test/bats](tests/bats) directory for more examples.

### Requirements

- fapolicyd 1.0
- Python 3.8
- Rust 1.52

### Developers

See the [Wiki](https://github.com/ctc-oss/fapolicy-analyzer/wiki) for more resources.
