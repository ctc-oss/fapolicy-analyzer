import logging
from redux import Reducer, Action, handle_actions
from typing import NamedTuple
from fapolicy_analyzer.ui.actions import (
    RECEIVED_DAEMON_START,
    RECEIVED_DAEMON_STOP,
    RECEIVED_DAEMON_STATUS,
    RECEIVED_DAEMON_RELOAD,
)
from fapolicy_analyzer import is_fapolicyd_active, Handle


class DaemonState(NamedTuple):
    error: str
    status: bool
    handle: Handle


def handle_received_daemon_start(state, action: Action):
    logging.debug("handle_received_daemon_start(state, action: Action):")
    payload = None
    return (*state, payload)


def handle_received_daemon_stop(state, action: Action):
    logging.debug("handle_received_daemon_stop(state, action: Action):")
    payload = None
    return (*state, payload)


def handle_received_daemon_reload(state, action: Action):
    logging.debug("handle_received_daemon_reload(state, action: Action):")
    payload = None
    return (*state, payload)


def handle_received_daemon_status(state, action: Action):
    logging.debug("handle_received_daemon_status(state, action: Action):")
    logging.debug("Fapolicyd daemon status: {}".format(is_fapolicyd_active()))
    payload = None
    return (*state, payload)


daemon_reducer: Reducer = handle_actions(
    {
        RECEIVED_DAEMON_START: handle_received_daemon_start,
        RECEIVED_DAEMON_STOP: handle_received_daemon_stop,
        RECEIVED_DAEMON_RELOAD: handle_received_daemon_reload,
        RECEIVED_DAEMON_STATUS: handle_received_daemon_status,
    },
    DaemonState(error=None, status=False, handle=None),
)
