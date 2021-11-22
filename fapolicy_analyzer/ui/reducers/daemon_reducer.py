import logging
from redux import Reducer, Action, handle_actions
from typing import NamedTuple, Optional, Any
from fapolicy_analyzer.ui.actions import (
    RECEIVED_DAEMON_START,
    RECEIVED_DAEMON_STOP,
    RECEIVED_DAEMON_STATUS,
    RECEIVED_DAEMON_RELOAD,
    RECEIVED_DAEMON_STATUS_UPDATE,
)
from fapolicy_analyzer import is_fapolicyd_active, Handle


class DaemonState(NamedTuple):
    error: str
    status: bool
    handle: Handle

def _create_state(state: DaemonState, **kwargs: Optional[Any]) -> DaemonState:
    return DaemonState(**{**state._asdict(), **kwargs})


def handle_received_daemon_start(state: DaemonState, action: Action):
    logging.debug("daemon_reducer::handle_received_daemon_start()")
    payload = None
    return (*state, payload)


def handle_received_daemon_stop(state: DaemonState, action: Action):
    logging.debug("daemon_reducer::handle_received_daemon_stop()")
    payload = None
    return (*state, payload)


def handle_received_daemon_reload(state: DaemonState, action: Action):
    logging.debug("daemon_reducer::handle_received_daemon_reload()")
    payload = None
    return (*state, payload)


def handle_received_daemon_status(state: DaemonState, action: Action):
    logging.debug(f"daemon_reducer::handle_received_daemon_status({state})")
    payload = None
    return (*state, payload)

def handle_received_daemon_status_update(state: DaemonState, action: Action):
    logging.debug(f"daemon_reducer::handle_received_daemon_status_update({state})")
    payload = None
    return _create_state(state, status=is_fapolicyd_active())

daemon_reducer: Reducer = handle_actions(
    {
        RECEIVED_DAEMON_START: handle_received_daemon_start,
        RECEIVED_DAEMON_STOP: handle_received_daemon_stop,
        RECEIVED_DAEMON_RELOAD: handle_received_daemon_reload,
        RECEIVED_DAEMON_STATUS: handle_received_daemon_status,
        RECEIVED_DAEMON_STATUS_UPDATE: handle_received_daemon_status_update,
    },
    DaemonState(error=None, status=False, handle=None),
)
