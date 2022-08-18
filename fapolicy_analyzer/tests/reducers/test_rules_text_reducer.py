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
from fapolicy_analyzer.ui.reducers.rules_text_reducer import (
    RulesTextState,
    handle_error_rules_text,
    handle_modify_rules_text,
    handle_received_rules_text,
    handle_request_rules_text,
)


@pytest.fixture()
def initial_state():
    return RulesTextState(
        error=None, rules_text="", loading=False, modified_rules_text=""
    )


def test_handle_request_rules_text(initial_state):
    result = handle_request_rules_text(initial_state, MagicMock())
    assert result == RulesTextState(
        error=None, rules_text="", loading=True, modified_rules_text=""
    )


def test_handle_received_rules_text(initial_state):
    result = handle_received_rules_text(initial_state, MagicMock(payload="foo"))
    assert result == RulesTextState(
        error=None, rules_text="foo", loading=False, modified_rules_text=""
    )


def test_handle_error_rules_text(initial_state):
    result = handle_error_rules_text(initial_state, MagicMock(payload="foo"))
    assert result == RulesTextState(
        error="foo", rules_text="", loading=False, modified_rules_text=""
    )


def test_handle_modify_rules_text(initial_state):
    result = handle_modify_rules_text(initial_state, MagicMock(payload="modified"))
    assert result == RulesTextState(
        error=None, rules_text="", loading=False, modified_rules_text="modified"
    )
