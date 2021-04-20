File Access Policy Analyzer
===

Tools to assist with the configuration and maintenance of [fapolicyd](https://github.com/linux-application-whitelisting/fapolicyd).

### Python bindings

We generate python bindings using [setuptools_rust](https://setuptools-rust.readthedocs.io/en/latest/) from the python directory.

```
pipenv install --dev
pipenv shell
python setup.py [develop | install]
python examples/validate_install.py
```

### Integration tests

We write integration tests using [Bats](https://bats-core.readthedocs.io/en/latest/index.html) and [Podman](https://podman.io/).  The integration tests can run locally or in Travis CI.

An example that demonstrates fapolicyd blocking execution, followed by a trust adjustment, followed by successful execution. 

```bash
@test "trust: add" {
  # initially denied :thumbs_down:
  run in_container /deny/simple.sh
  assert_output --partial "permission denied"

  # add a trust entry for the script
  run in_container python3 examples/add_trust.py /deny/simple.sh
  assert_output --partial "applying"
  assert_output --partial "signaling"

  # check the db for the script
  run in_container python3 examples/show_ancillary.py
  assert_output --partial "/deny/simple.sh"

  # now its runs :thumbs_up:
  run in_container /deny/simple.sh
  assert_output "OK"
}
```

See the [test/bats](tests/bats) directory for more examples.

### Developers
See the [Wiki](https://github.com/ctc-oss/fapolicy-analyzer/wiki) for more resources.
