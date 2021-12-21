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

import logging
from redux import Reducer, Action, handle_actions
from typing import Optional, Any
from fapolicy_analyzer.ui.actions import (
    RECEIVED_DAEMON_START,
    RECEIVED_DAEMON_STOP,
    RECEIVED_DAEMON_STATUS_UPDATE,
    DaemonState,
    ServiceStatus,
)


def _create_state(state: DaemonState, **kwargs: Optional[Any]) -> DaemonState:
    return DaemonState(**{**state._asdict(), **kwargs})


def handle_received_daemon_start(state: DaemonState, action: Action):
    logging.debug("daemon_reducer::handle_received_daemon_start()")
    return _create_state(state, status=action.payload)


def handle_received_daemon_stop(state: DaemonState, action: Action):
    logging.debug("daemon_reducer::handle_received_daemon_stop()")
    return _create_state(state, status=action.payload)


def handle_received_daemon_status_update(state: DaemonState, action: Action):
    logging.debug(f"daemon_reducer::handle_received_daemon_status_update({state}), {action}")
    return _create_state(state, status=action.payload.status,
                         error=action.payload.error)


daemon_reducer: Reducer = handle_actions(
    {
        RECEIVED_DAEMON_START: handle_received_daemon_start,
        RECEIVED_DAEMON_STOP: handle_received_daemon_stop,
        RECEIVED_DAEMON_STATUS_UPDATE: handle_received_daemon_status_update,
    },
    DaemonState(error=None, status=ServiceStatus.UNKNOWN),
)
