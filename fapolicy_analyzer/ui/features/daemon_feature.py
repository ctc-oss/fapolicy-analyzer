import gi
import os
import logging
import sys
from time import sleep
from threading import Thread

gi.require_version("Gtk", "3.0")
from fapolicy_analyzer import (
    Handle,
)

from fapolicy_analyzer.ui.actions import (
    REQUEST_DAEMON_START,
    REQUEST_DAEMON_STOP,
    REQUEST_DAEMON_RELOAD,
    REQUEST_DAEMON_STATUS_UPDATE,
    error_daemon_reload,
    error_daemon_start,
    error_daemon_status_update,
    error_daemon_stop,
    init_daemon,
    received_daemon_reload,
    received_daemon_start,
    received_daemon_status_update,
    received_daemon_stop,
    DaemonState,
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
from fapolicy_analyzer.ui.strings import DAEMON_INITIALIZATION_ERROR
from rx import of, pipe
from rx.operators import catch, map
from typing import Callable

DAEMON_FEATURE = "daemon"
_fapd_status: bool = False
_fapd_ref: Handle = None


def create_daemon_feature(dispatch: Callable, daemon=None) -> ReduxFeatureModule:
    """
    Creates a Redux feature of type Daemon

    Keyword arguments:
    dispatch -- the Redux Store dispatch method, used for dispatching actions
    daemon -- the fapolicy_analyzer.daemon object, defaults to None. If not
    provided, a new Daemon object will be initialized.  Used for testing
    purposes only.
    """
    def _init_daemon() -> Action:
        logging.debug("_init_daemon() -> Action")

        def acquire_daemon():
            logging.debug("acquire_daemon()")
            try:
                daemon = Handle("fapolicyd")
                finish(daemon)
            except RuntimeError:
                logging.exception(DAEMON_INITIALIZATION_ERROR)
                GLib.idle_add(sys.exit, 1)

        def monitor_daemon(timeout=5):
            global _fapd_ref, _fapd_status
            while True:
                bStatus = _fapd_ref.is_active()
                if(bStatus != _fapd_status):
                    logging.debug("monitor_daemon():Dispatching update request")
                    _fapd_status = bStatus
                    dispatch(received_daemon_status_update(DaemonState(
                        status=_fapd_status,
                        handle=_fapd_ref,
                        error=None
                    )))
                sleep(timeout)

        def start_daemon_monitor():
            logging.debug("start_daemon_monitor()")
            thread = Thread(target=monitor_daemon)
            thread.daemon = True
            thread.start()

        def finish(daemon: Handle):
            global _fapd_ref, _fapd_status
            logging.debug(f"daemon_feature::finish({daemon})")
            _fapd_ref = daemon
            _fapd_status = _fapd_ref.is_active()
            dispatch(received_daemon_status_update(DaemonState(
                status=_fapd_status,
                handle=_fapd_ref,
                error=None
            )))

        if daemon:
            finish(daemon)
        else:
            acquire_daemon()

        if "NO_DAEMON_MONITORING" not in os.environ:
            start_daemon_monitor()

        return init_daemon()

    def _daemon_reload(action: Action) -> Action:
        logging.debug("_daemon_reload(action: Action) -> Action")
        return received_daemon_reload()

    def _daemon_start(action: Action) -> Action:
        logging.debug("_daemon_start(action: Action) -> Action")
        _fapd_ref.start()
        return received_daemon_start()

    def _daemon_status_update(action: Action) -> Action:
        _fapd_status = _fapd_ref.is_active()
        logging.debug(f"_daemon_status_update({action}): status:{_fapd_status}")
        return received_daemon_status_update(_fapd_status)

    def _daemon_stop(action: Action) -> Action:
        logging.debug("_daemon_stop(action: Action) -> Action")
        _fapd_ref.stop()
        return received_daemon_stop()

    init_epic = pipe(
        of_init_feature(DAEMON_FEATURE),
        map(lambda _: _init_daemon()),
    )

    request_daemon_reload_epic = pipe(
        of_type(REQUEST_DAEMON_RELOAD),
        map(_daemon_reload),
        catch(lambda ex, source: of(error_daemon_reload(str(ex)))),
    )

    request_daemon_start_epic = pipe(
        of_type(REQUEST_DAEMON_START),
        map(_daemon_start),
        catch(lambda ex, source: of(error_daemon_start(str(ex)))),
    )

    request_daemon_status_update_epic = pipe(
        of_type(REQUEST_DAEMON_STATUS_UPDATE),
        map(_daemon_status_update),
        catch(lambda ex, source: of(error_daemon_status_update(str(ex)))),
    )

    request_daemon_stop_epic = pipe(
        of_type(REQUEST_DAEMON_STOP),
        map(_daemon_stop),
        catch(lambda ex, source: of(error_daemon_stop(str(ex)))),
    )

    daemon_epic = combine_epics(
        init_epic,
        request_daemon_reload_epic,
        request_daemon_start_epic,
        request_daemon_status_update_epic,
        request_daemon_stop_epic,
    )

    return create_feature_module(DAEMON_FEATURE,
                                 daemon_reducer,
                                 epic=daemon_epic,
                                 )
