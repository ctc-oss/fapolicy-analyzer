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

list:
	@echo
	@echo "  Usage: make [target]"
	@echo
	@echo "       fapolicy-analyzer - High level common operation targets"
	@echo
	@echo "     list    - Display common development targets"
	@echo "     dev-shell  - Install deps, build bindings, start venv shell"
	@echo "     run     - Execute the fapolicy-analyzer"
	@echo "     listall - Display all targets"
	@echo "    "

###############################################################################
# Development environment population and creation
dev-shell: pipenv-install pybindings
	@echo
	@echo "--- Starting a fapolicy-analyzer development shell"
	pipenv shell
	@echo "--- Development shell terminated"

dev-env: pipenv-install pybindings

pipenv-install:
	@echo "  |--- Installing pipenv dependencies..."
	pipenv install --dev

pybindings: pipenv-install
	@echo "  |--- Generating python bindings..."
	pipenv run python setup.py develop

###############################################################################
# fapolicy-analyzer execution
run: dev-env
	pipenv run python -m fapolicy_analyzer.ui

run-verbose: dev-env
	pipenv run python -m fapolicy_analyzer.ui -v

###############################################################################
# Development unit-testing and source code style tools
test: 
	@echo "--- Invoking pytest unit-test suite"
	pipenv run xvfb-run -a pytest -s --cov fapolicy_analyzer/

format: pyformat rsformat
	@echo "--- Invoking formatting tools"

pyformat:
	pipenv run black fapolicy_analyzer/

rsformat:
	pipenv run cargo fmt

lint: pylint rslint
	@echo "--- Source linting completed"

pylint:
	@echo "  |--- Python linting..."
	pipenv run flake8 fapolicy_analyzer/

rslint:
	@echo "  |--- Rust linting..."
	pipenv run cargo clippy --all


pushprep: format lint test
	@echo "--- Pre-Push checks"
	git status

