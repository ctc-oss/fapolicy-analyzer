import gi
import logging
import sys

gi.require_version("Gtk", "3.0")

from fapolicy_analyzer.ui.actions import (
    REQUEST_DAEMON_START,
    REQUEST_DAEMON_STOP,
    REQUEST_DAEMON_RELOAD,
    REQUEST_DAEMON_STATUS,
    error_daemon_start,
    error_daemon_stop,
    error_daemon_reload,
    error_daemon_status,
    received_daemon_start,
    received_daemon_stop,
    received_daemon_reload,
    received_daemon_status,
)
from fapolicy_analyzer.ui.reducers import daemon_reducer
from gi.repository import GLib
from redux import (
    Action,
    combine_epics,
    create_feature_module,
    of_init_feature,
    of_type,
    ReduxFeatureModule,
)
from rx import of, pipe
from rx.operators import catch, ignore_elements, map
from typing import Callable, Sequence

DAEMON_FEATURE = "daemon"

def create_daemon_feature(dispatch: Callable, daemon=None) -> ReduxFeatureModule:
    """
    Creates a Redux feature of type Daemon

    Keyword arguments:
    dispatch -- the Redux Store dispatch method, used for dispatching actions
    daemon -- the fapolicy_analyzer.daemon object, defaults to None. If not 
    provided, a new Daemon object will be initialized.  Used for testing 
    purposes only.
    """
 
    def _request_daemon_status(action: Action) -> Action:
        breakpoint()
        return received_daemon_status()


    def _request_daemon_reload(action: Action) -> Action:
        return received_daemon_reload()


    def _request_daemon_start(action: Action) -> Action:
        return received_daemon_start()


    def _request_daemon_stop(action: Action) -> Action:
        return received_daemon_stop()


    return create_feature_module(DAEMON_FEATURE)
