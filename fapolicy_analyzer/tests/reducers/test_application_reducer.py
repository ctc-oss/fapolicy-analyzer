# Copyright Concurrent Technologies Corporation 2023
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

from fapolicy_analyzer.ui.reducers.application_reducer import (
    AppConfigState,
    handle_error_app_config,
    handle_received_app_config,
    handle_request_app_config,
)
from fapolicy_analyzer.ui.types import PAGE_SELECTION


@pytest.fixture()
def initial_state():
    return AppConfigState(
        loading=False, initial_view=PAGE_SELECTION.RULES_ADMIN, error=None
    )


def test_handle_request_app_config(initial_state):
    result = handle_request_app_config(initial_state, MagicMock())
    assert result == AppConfigState(
        loading=True, initial_view=PAGE_SELECTION.RULES_ADMIN, error=None
    )


def test_handle_receive_app_config(initial_state):
    result = handle_received_app_config(
        initial_state, MagicMock(payload={"initial_view": PAGE_SELECTION.PROFILER})
    )
    assert result == AppConfigState(
        loading=False, initial_view=PAGE_SELECTION.PROFILER, error=None
    )


def test_handle_error_app_config(initial_state):
    result = handle_error_app_config(initial_state, MagicMock(payload="foo"))
    assert result == AppConfigState(
        loading=False, initial_view=PAGE_SELECTION.RULES_ADMIN, error="foo"
    )
