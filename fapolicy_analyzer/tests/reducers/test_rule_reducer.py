# Copyright Concurrent Technologies Corporation 2022
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

import context  # noqa: F401
import pytest
from fapolicy_analyzer.ui.reducers.rule_reducer import (
    RuleState,
    handle_error_rules,
    handle_received_rules,
    handle_request_rules,
)


@pytest.fixture()
def initial_state():
    return RuleState(error=None, rules=[], loading=False)


def test_handle_request_rules(initial_state):
    result = handle_request_rules(initial_state, MagicMock())
    assert result == RuleState(error=None, rules=[], loading=True)


def test_handle_received_rules(initial_state):
    result = handle_received_rules(initial_state, MagicMock(payload=["foo"]))
    assert result == RuleState(error=None, rules=["foo"], loading=False)


def test_handle_error_rules(initial_state):
    result = handle_error_rules(initial_state, MagicMock(payload="foo"))
    assert result == RuleState(error="foo", rules=[], loading=False)
