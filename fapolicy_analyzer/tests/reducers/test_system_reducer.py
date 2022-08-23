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

import context  # noqa: F401 # isort: skip
from unittest.mock import MagicMock

import pytest
from fapolicy_analyzer.ui.reducers.system_reducer import (
    SystemState,
    handle_add_changesets,
    handle_clear_changesets,
    handle_error_deploying_system,
    handle_error_system_initialization,
    handle_system_checkpoint_set,
    handle_system_deployed,
    handle_system_received,
)


@pytest.fixture()
def initial_state():
    return SystemState(error=None, system=None, checkpoint=None, deployed=False)


def test_handle_system_received(initial_state):
    mock_system = MagicMock()
    result = handle_system_received(initial_state, MagicMock(payload=mock_system))
    assert result == SystemState(
        error=None, system=mock_system, checkpoint=None, deployed=False
    )


def test_handle_error_system_initialization(initial_state):
    result = handle_error_system_initialization(initial_state, MagicMock(payload="foo"))
    assert result == SystemState(
        error="foo", system=None, checkpoint=None, deployed=False
    )


def test_handle_system_checkpoint_set(initial_state):
    mock_checkpoint = MagicMock()
    result = handle_system_checkpoint_set(
        initial_state, MagicMock(payload=mock_checkpoint)
    )
    assert result == SystemState(
        error=None, system=None, checkpoint=mock_checkpoint, deployed=False
    )


def test_handle_system_deployed(initial_state):
    result = handle_system_deployed(initial_state, MagicMock())
    assert result == SystemState(
        error=None, system=None, checkpoint=None, deployed=True
    )


def test_handle_error_deploying_system(initial_state):
    result = handle_error_deploying_system(initial_state, MagicMock(payload="foo"))
    assert result == SystemState(
        error="foo", system=None, checkpoint=None, deployed=False
    )


def test_handle_add_changesets(initial_state):
    result = handle_add_changesets(initial_state, MagicMock())
    assert result == SystemState(
        error=None, system=None, checkpoint=None, deployed=False
    )


def test_handle_clear_changesets(initial_state):
    result = handle_clear_changesets(initial_state, MagicMock())
    assert result == SystemState(
        error=None, system=None, checkpoint=None, deployed=True
    )
