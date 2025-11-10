# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Makefile -  execution wrapper for common fapolicy-analyzer development tasks
#
# Developer note: If any new targets are added to this file, pls add a
#   description comment immediately preceding the target:dependency line so
#   that the list-all extraction scripting can work correctly.
#
PYBABEL = uv run pybabel
DOMAIN  = fapolicy-analyzer
LOCALEDIR = locale
BABEL_MAPPING = babel.cfg
BABEL_INPUTDIRS = fapolicy_analyzer/ui fapolicy_analyzer/glade
POTFILE  = $(LOCALEDIR)/$(DOMAIN).pot

GRN=\033[0;32m
RED=\033[0;31m
NC=\033[0m # No Color

VERSION ?= $(shell sed -n 's/^Version: *//p' fapolicy-analyzer.spec)
fc      ?= rawhide
el      ?= 9

# List the common developer targets
list:
	@echo
	@echo "  Usage: make [target]"
	@echo
	@echo "       fapolicy-analyzer - High level common operation targets"
	@echo
	@echo "     run      - Execute the fapolicy-analyzer"
	@echo "     test     - Execute all unit-tests"
	@echo "     lint     - Execute source code linting tools"
	@echo "     format   - Execute source code formatting"
	@echo "     check    - Perform pre-git push tests and formatting"
	@echo
	@echo "     Note: Options can be passed to fapolicy-analyzer by"
	@echo "           setting the OPTIONS environment variable, for example"
	@echo "             $$ OPTIONS='-v' make run"
	@echo
	@echo "     Note: Errors stop make, ignore them with the '-k' option:"
	@echo "             $$ make -k [target]"
	@echo

# extract and compile
i18n: i18n-extract i18n-compile

# Extract translatable strings from source
i18n-extract:
	$(PYBABEL) extract -F $(BABEL_MAPPING) -o $(POTFILE) $(BABEL_INPUTDIRS)

# Update existing .po files (if any)
i18n-update: i18n-extract
	$(PYBABEL) update -i $(POTFILE) -d $(LOCALEDIR) -D $(DOMAIN)

# Compile .po → .mo files for all locales
i18n-compile:
	$(PYBABEL) compile -d $(LOCALEDIR) -D $(DOMAIN)

i18n-clean:
	rm -f $(POTFILE)
	find $(LOCALEDIR) -name '*.mo' -delete

# Build the python/rust bindings
build:
	@echo -e "${GRN}  |--- Generating python bindings...${NC}"
	uv run maturin develop

###############################################################################
# fapolicy-analyzer execution
# Execute fapolicy-analyzer [OPTIONS]
run: build
	uv run gui

###############################################################################
# Development unit-testing and source code style tools
# Execute the full unit-test suite
test: pytest cargo-test
	@echo -e "${GRN}--- Testing complete.${NC}"

# Execute the python unit tests
pytest: build
	@echo -e "${GRN}  |--- Python unit-testing: Invoking pytest...${NC}"
	uv run xvfb-run -a pytest -s --cov=fapolicy_analyzer fapolicy_analyzer/tests/

# Execute the Rust unit-tests
cargo-test: build
	@echo -e "${GRN}  |--- Rust unit-testing: Invoking cargo test...${NC}"
	cargo test --all

# Format project source code
format: pyformat cargo-fmt
	@echo -e "${GRN}--- Formatting complete${NC}"

# Format python source code
pyformat:
	@echo -e "${GRN}  |--- Python formating...${NC}"
	uv run ruff format

# Format rust source code
cargo-fmt:
	@echo -e "${GRN}-  |--- Rust formatting...${NC}"
	cargo fmt

# Perform linting on the project source code
lint: pylint clippy
	@echo -e "${GRN}--- Source linting complete${NC}"

# Ensure header exists on required files
header-check:
	@ grep -R -L --exclude-dir=vendor \
        --include='*.py' --include='*.rs' --include='*.glade' --include='*.sh' \
        --exclude-dir 'target' \
        'Copyright Concurrent Technologies Corporation' *

# Perform linting on the Python source code
pylint:
	@echo -e "${GRN}-  |--- Python linting...${NC}"
	uv run ruff check fapolicy_analyzer

# Perform linting on the rust source code
clippy:
	@echo -e "${GRN}-  |--- Rust linting...${NC}"
	cargo clippy --all

# Perform pre- git push unit-testing, formating, and linting
check: header-check format lint test
	@echo -e "${GRN}--- Pre-Push checks complete${NC}"
	git status

# Execute the commands to generate the build information for display
build-info:
	@echo -e "${GRN}-  |--- Build info created${NC}"
	uv run scripts/build-info.py --git --os --time

# Generate Fedora rawhide rpms
fc-rpm:
	@echo -e "${GRN}--- Fedora $(fc) RPM generation v${VERSION}...${NC}"
	make -f .copr/Makefile vendor OS_ID=fedora VERSION=${VERSION}
	podman build -t fapolicy-analyzer:build-fc$(fc) --target fedorabuild --build-arg version=${VERSION} -f Containerfile .
	podman run --privileged --rm -it -v /tmp:/v fapolicy-analyzer:build-fc$(fc) fedora-$(fc)-x86_64 /v

# Generate RHEL 9 rpms
el-rpm:
	@echo -e "${GRN}--- el$(el) RPM generation v${VERSION}...${NC}"
	make -f .copr/Makefile vendor vendor-rs OS_ID=rhel VERSION=${VERSION} DIST=.el$(el) spec=scripts/srpm/fapolicy-analyzer.el$(el).spec
	podman build -t fapolicy-analyzer:build-el$(el) --target elbuild --build-arg version=${VERSION} --build-arg spec=scripts/srpm/fapolicy-analyzer.el$(el).spec -f Containerfile .
	podman run --privileged --rm -it -v /tmp:/v fapolicy-analyzer:build-el$(el) rocky+epel-$(el)-x86_64 /v

# Update embedded help documentation
help-docs:
	uv run help update
	uv run help build

# Update the project version using git describe version string
version-string:
	uv run scripts/version.py --patch --toml $(PWD)/pyproject.toml

# Remove build related temporary files
clean:
	@rm -rf ./build/
	@rm -rf ./vendor-rs/
	@rm -f  ./fapolicy_analyzer/resources/build-info.json

# Clean all build caches and build related temporary files
clean-all: clean
	@uv clean -q
	@cargo clean -q
