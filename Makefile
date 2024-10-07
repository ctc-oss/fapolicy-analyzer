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
GRN=\033[0;32m
RED=\033[0;31m
NC=\033[0m # No Color

VERSION ?= $(shell sed -n 's/^Version: *//p' fapolicy-analyzer.spec)

# List the common developer targets
list:
	@echo
	@echo "  Usage: make [target]"
	@echo
	@echo "       fapolicy-analyzer - High level common operation targets"
	@echo
	@echo "     list     - Display common development targets"
	@echo "     shell    - Install deps, build bindings, start venv shell"
	@echo "     run      - Execute the fapolicy-analyzer"
	@echo "     test     - Execute all unit-tests"
	@echo "     lint     - Execute source code linting tools"
	@echo "     format   - Execute source code formatting"
	@echo "     check    - Perform pre-git push tests and formatting"
	@echo "     list-all - Display all targets"
	@echo
	@echo "     Note: Options can be passed to fapolicy-analyzer by"
	@echo "           setting the OPTIONS environment variable, for example"
	@echo "             $$ OPTIONS='-v' make run"
	@echo
	@echo "     Note: Errors stop make, ignore them with the '-k' option:"
	@echo "             $$ make -k [target]"
	@echo

###############################################################################
# Development environment population and creation
# Start a shell session in a python virtual environment
shell: install build
	@echo
	@echo -e "${GRN}--- Starting a fapolicy-analyzer development shell${NC}"
	pipenv shell
	@echo -e "${GRN}--- Development shell terminated${NC}"

# Update the virtual environment suitable for pipenv run
env: install build
	@echo -e "${GRN}--- Updating the virtual environment complete${NC}"

# Install python dependencies into the virtual environment
install:
	@echo -e "${GRN}  |--- Installing pipenv dependencies...${NC}"
	pipenv install --dev

# Build the python/rust bindings
build: install
	@echo -e "${GRN}  |--- Generating python bindings...${NC}"
	pipenv run python setup.py develop

###############################################################################
# fapolicy-analyzer execution
# Execute fapolicy-analyzer [OPTIONS]
run: env
	pipenv run python -m fapolicy_analyzer.ui ${OPTIONS}

###############################################################################
# Development unit-testing and source code style tools
# Execute the full unit-test suite
test: pytest cargo-test
	@echo -e "${GRN}--- Testing complete.${NC}"

# Execute the python unit tests
pytest: build
	@echo -e "${GRN}  |--- Python unit-testing: Invoking pytest...${NC}"
	pipenv run xvfb-run -a pytest -s --cov=fapolicy_analyzer fapolicy_analyzer/tests/

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
	pipenv run format

# Format rust source code
cargo-fmt:
	@echo -e "${GRN}-  |--- Rust formatting...${NC}"
	pipenv run cargo fmt

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
	pipenv run lint

# Perform linting on the rust source code
clippy:
	@echo -e "${GRN}-  |--- Rust linting...${NC}"
	pipenv run cargo clippy --all

# Perform pre- git push unit-testing, formating, and linting
check: header-check format lint test
	@echo -e "${GRN}--- Pre-Push checks complete${NC}"
	git status

# Execute the commands to generate the build information for display
build-info:
	@echo -e "${GRN}-  |--- Build info created${NC}"
	scripts/build-info.py --overwrite --git --os --time

# Generate Fedora rawhide rpms
fc-rpm:
	@echo -e "${GRN}--- Fedora RPM generation v${VERSION}...${NC}"
	make -f .copr/Makefile vendor OS_ID=fedora VERSION=${VERSION}
	podman build -t fapolicy-analyzer:build --target fedorabuild --build-arg version=${VERSION} -f Containerfile .
	podman run --privileged --rm -it -v /tmp:/v fapolicy-analyzer:build fedora-39-x86_64 /v

# Generate RHEL 9 rpms
el9-rpm:
	@echo -e "${GRN}--- el9 RPM generation v${VERSION}...${NC}"
	make -f .copr/Makefile vendor vendor-rs OS_ID=rhel VERSION=${VERSION} DIST=.el9 spec=scripts/srpm/fapolicy-analyzer.el9.spec
	podman build -t fapolicy-analyzer:build --target elbuild --build-arg version=${VERSION} --build-arg spec=scripts/srpm/fapolicy-analyzer.el9.spec -f Containerfile .
	podman run --privileged --rm -it -v /tmp:/v fapolicy-analyzer:build rocky+epel-9-x86_64 /v

# Update embedded help documentation
help-docs:
	python3 help update
	python3 help build

# Display all Makefile targets
list-all:
	@echo
	@echo -e "${GRN}---Displaying all fapolicy-analyzer targets${NC}"
	@echo
	# Input to the loop is a list of targets extracted from this Makefile
	@for t in `grep -E -o '^[^#].+*:' Makefile | egrep -v 'echo|@|podman'`;\
	do # Output the target w/o a newline\
	echo -e -n "$$t    \t";\
	# grep the Makefile for the target; print line immediately preceding it\
	grep  -B1 "^$$t" Makefile | head -1 | sed 's/\#//';\
	done
	@echo
