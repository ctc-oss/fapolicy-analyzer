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

import context  # noqa: F401
import pytest
from unittest.mock import MagicMock
from fapolicy_analyzer.ui.reducers.group_reducer import (
    GroupState,
    handle_error_groups,
    handle_received_groups,
    handle_request_groups,
)


@pytest.fixture()
def initial_state():
    return GroupState(error=None, groups=[], loading=False)


def test_handle_request_groups(initial_state):
    result = handle_request_groups(initial_state, MagicMock())
    assert result == GroupState(error=None, groups=[], loading=True)


def test_handle_received_groups(initial_state):
    result = handle_received_groups(initial_state, MagicMock(payload=["foo"]))
    assert result == GroupState(error=None, groups=["foo"], loading=False)


def test_handle_error_groups(initial_state):
    result = handle_error_groups(initial_state, MagicMock(payload="foo"))
    assert result == GroupState(error="foo", groups=[], loading=False)
