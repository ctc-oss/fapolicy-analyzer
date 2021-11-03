import logging
from redux import Reducer, Action, handle_actions
from .ancillary_trust_reducer import ancillary_trust_reducer
from .event_reducer import event_reducer
from fapolicy_analyzer.ui.actions import (
    REQUEST_DAEMON_START,
    REQUEST_DAEMON_STOP,
    REQUEST_DAEMON_STATUS,
    REQUEST_DAEMON_RELOAD,
)

def handle_request_daemon_start( state, action: Action):
    logging.debug("handle_request_daemon_start( state, action: Action):")
    payload = None
    return (*state, payload)

def handle_request_daemon_stop( state, action: Action):
    logging.debug("handle_request_daemon_stop( state, action: Action):")
    payload = None
    return (*state, payload)

def handle_request_daemon_reload( state, action: Action):
    logging.debug("handle_request_daemon_reload( state, action: Action):")
    payload = None
    return (*state, payload)

def handle_request_daemon_status( state, action: Action):
    logging.debug("handle_request_daemon_status( state, action: Action):")
    payload = None
    return (*state, payload)

daemon_reducer: Reducer = handle_actions(
    {
        REQUEST_DAEMON_START: handle_request_daemon_start,
        REQUEST_DAEMON_STOP: handle_request_daemon_stop,
        REQUEST_DAEMON_RELOAD: handle_request_daemon_reload,
        REQUEST_DAEMON_STATUS: handle_request_daemon_status,
    },
    [],
)

