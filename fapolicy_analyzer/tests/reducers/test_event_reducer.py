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
from ui.reducers.event_reducer import (
    EventState,
    handle_error_events,
    handle_received_events,
    handle_request_events,
)


@pytest.fixture()
def initial_state():
    return EventState(error=None, log=[], loading=False)


def test_handle_request_events(initial_state):
    result = handle_request_events(initial_state, MagicMock())
    assert result == EventState(error=None, log=[], loading=True)


def test_handle_received_events(initial_state):
    result = handle_received_events(initial_state, MagicMock(payload=["foo"]))
    assert result == EventState(error=None, log=["foo"], loading=False)


def test_handle_error_events(initial_state):
    result = handle_error_events(initial_state, MagicMock(payload="foo"))
    assert result == EventState(error="foo", log=[], loading=False)
