# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
import context  # noqa: F401
import pytest
from unittest.mock import MagicMock
from ui.reducers.user_reducer import (
    UserState,
    handle_error_users,
    handle_received_users,
    handle_request_users,
)


@pytest.fixture()
def initial_state():
    return UserState(error=None, users=[], loading=False)


def test_handle_request_users(initial_state):
    result = handle_request_users(initial_state, MagicMock())
    assert result == UserState(error=None, users=[], loading=True)


def test_handle_received_users(initial_state):
    result = handle_received_users(initial_state, MagicMock(payload=["foo"]))
    assert result == UserState(error=None, users=["foo"], loading=False)


def test_handle_error_users(initial_state):
    result = handle_error_users(initial_state, MagicMock(payload="foo"))
    assert result == UserState(error="foo", users=[], loading=False)
