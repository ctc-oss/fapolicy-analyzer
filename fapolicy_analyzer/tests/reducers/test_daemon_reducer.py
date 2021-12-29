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
from ui.reducers.daemon_reducer import (
    handle_received_daemon_start,
    handle_received_daemon_stop,
    handle_received_daemon_status_update,
)
from fapolicy_analyzer.ui.actions import (
    DaemonState,
    ServiceStatus,
)


@pytest.fixture()
def initial_state():
    return DaemonState(error=None, status=ServiceStatus.UNKNOWN)


def test_handle_received_daemon_start(initial_state):
    result = handle_received_daemon_start(
        initial_state,
        MagicMock(payload=DaemonState(error=None, status=ServiceStatus.UNKNOWN)),
    )
    print(result)
    assert result == DaemonState(error=None, status=ServiceStatus.UNKNOWN)


def test_handle_received_daemon_stop(initial_state):
    result = handle_received_daemon_stop(
        initial_state,
        MagicMock(payload=DaemonState(error=None, status=ServiceStatus.UNKNOWN)),
    )
    assert result == DaemonState(error=None, status=ServiceStatus.UNKNOWN)


def test_handle_received_daemon_status_update(initial_state):
    result = handle_received_daemon_status_update(
        initial_state,
        MagicMock(payload=DaemonState(error=None, status=ServiceStatus.TRUE)),
    )
    assert result == DaemonState(error=None, status=ServiceStatus.TRUE)
