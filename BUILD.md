Building
===

The build of fapolicy-analyzer and its command line utilities uses Maturin and uv. The environment will run out of a
Python virtual environment. The setup process is as follows.

## Steps
1. Install uv - `pip install uv`
2. Create venv - `uv venv`
3. Install maturin - `uv pip install maturin`
4. Install dependencies - `uv sync`
5. Build fapolicy-analyzer - `uv run maturin develop`
6. Launch fapolicy-analzyer - `uv run gui`

## Python Requirements

The minimum supported Python version is 3.9

See the [pyproject.toml](pyproject.toml) for project dependencies.

## Rust Requirements

The minimum supported Rust version is 1.84.1

See the Cargo.toml files in each individual [crate](crates) for detailed Rust dependencies.

## System Dependencies

### Build
- python3-devel
- python3-setuptools
- python3-setuptools-rust
- python3-pip
- python3-wheel
- python3-babel
- dbus-devel
- gettext
- itstool
- desktop-file-utils
- clang
- audit-libs-devel
- lmdb-devel

### Run tests

- python3-gobject
- python3-configargparse
- python3-more-itertools
- python3-rx
- python3-tomli
- gtk3
- gtksourceview3
- gnome-icon-theme
