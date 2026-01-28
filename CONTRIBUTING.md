Contributing Guide
===

Thank you for your efforts to improve the fapolicy-analyzer project. This guide
will help you regarding various aspects like submitting issues, contributing a
feature, etc.

### Building

See [BUILD.md](BUILD.md) for development environment setup.

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

### Changelog updates

We use [towncrier](https://towncrier.readthedocs.io/en/stable/index.html) to generate a CHANGELOG for each release.

To include your change in the release notes please create a news article in the `news` directory.

Valid articles should be saved as `<PR>.<CATEGORY>.md` where `<PR>` is the pull request number and `<CATEGORY>` is one of:

- `fixed` - for bug fixes
- `added` - added a new feature
- `changed` - changed an existing feature
- `removed` - removed capability
- `packaging` - an RPM or dependency changes

PRs may be excluded from the documentation requirement if they fall into one of the following categories:

- `ci` - Continuous Integration changes do not need reported to users
- `documentation` - Documentation improvements do not usually need reported to users
- `release` - Release PRs do not need a news article

To exclude the news check on a PR label the PR with the category or tag PR title with a prefix + `:`, eg. `ci: Updated the build`.

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
