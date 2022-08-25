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
from fapolicy_analyzer.ui.reducers.ancillary_trust_reducer import (
    TrustState,
    handle_error_ancillary_trust,
    handle_received_ancillary_trust,
    handle_request_ancillary_trust,
)


@pytest.fixture()
def initial_state():
    return TrustState(error=None, trust=[], loading=False)


def test_handle_request_ancillary_trust(initial_state):
    result = handle_request_ancillary_trust(initial_state, MagicMock())
    assert result == TrustState(error=None, trust=[], loading=True)


def test_handle_received_ancillary_trust(initial_state):
    result = handle_received_ancillary_trust(initial_state, MagicMock(payload=["foo"]))
    assert result == TrustState(error=None, trust=["foo"], loading=False)


def test_handle_error_ancillary_trust(initial_state):
    result = handle_error_ancillary_trust(initial_state, MagicMock(payload="foo"))
    assert result == TrustState(error="foo", trust=[], loading=False)
