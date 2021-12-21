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

from unittest.mock import MagicMock

import pytest
from fapolicy_analyzer.ui.operations.ui_operation import UIOperation


@pytest.fixture
def op():
    # trick it into thinking there are no abstract methods
    UIOperation.__abstractmethods__ = set()
    return UIOperation()


def test_get_text(op):
    assert op.get_text() is None


def test_get_icon(op):
    assert op.get_icon() is None


def test_run(op):
    assert op.run() is None


def test_dispose(op):
    assert op.dispose() is None


def test_calls_dispose():
    mock_cleanup = MagicMock()

    def dispose():
        mock_cleanup()

    UIOperation.__abstractmethods__ = set()
    with UIOperation() as op:
        op.dispose = dispose
    mock_cleanup.assert_called_once()
