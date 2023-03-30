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

import context  # noqa: F401 # isort: skip
from unittest.mock import MagicMock

import pytest

from fapolicy_analyzer.ui.reducers.trust_reducer import (
    TrustState,
    handle_error_trust,
    handle_received_trust_update,
    handle_request_trust,
    handle_trust_load_complete,
    handle_trust_load_started,
)


@pytest.fixture()
def initial_state():
    return TrustState(
        error=None,
        trust=[],
        loading=False,
        percent_complete=-1,
        last_set_completed=None,
        trust_count=0,
    )


def test_handle_request_trust(initial_state):
    result = handle_request_trust(initial_state, MagicMock())
    assert result == TrustState(
        error=None,
        trust=[],
        loading=True,
        percent_complete=-1,
        last_set_completed=None,
        trust_count=0,
    )


def test_handle_trust_load_started(initial_state):
    result = handle_trust_load_started(initial_state, MagicMock(payload=1))
    assert result == TrustState(
        error=None,
        trust=[],
        loading=True,
        percent_complete=0,
        last_set_completed=None,
        trust_count=1,
    )


def test_handle_received_trust_update(initial_state):
    current_trust = [MagicMock()]
    trust_update = [MagicMock()]
    incoming_state = TrustState(
        **{
            **initial_state._asdict(),
            "trust": current_trust,
            "trust_count": 2,
            "loading": True,
        }
    )
    result = handle_received_trust_update(
        incoming_state, MagicMock(payload=(trust_update, 2))
    )
    assert result == TrustState(
        error=None,
        trust=[*current_trust, *trust_update],
        loading=True,
        percent_complete=100,
        last_set_completed=trust_update,
        trust_count=2,
    )


def test_handle_trust_load_complete(initial_state):
    trust = [MagicMock()]
    incoming_state = TrustState(
        **{
            **initial_state._asdict(),
            "trust": trust,
            "trust_count": 1,
            "loading": True,
            "last_set_completed": [],
            "percent_complete": 100,
        }
    )
    result = handle_trust_load_complete(incoming_state, MagicMock())
    assert result == TrustState(
        error=None,
        loading=False,
        trust=trust,
        percent_complete=100,
        last_set_completed=None,
        trust_count=1,
    )


def test_handle_error_trust(initial_state):
    result = handle_error_trust(initial_state, MagicMock(payload="foo"))
    assert result == TrustState(
        error="foo",
        trust=[],
        loading=False,
        percent_complete=-1,
        last_set_completed=None,
        trust_count=0,
    )
