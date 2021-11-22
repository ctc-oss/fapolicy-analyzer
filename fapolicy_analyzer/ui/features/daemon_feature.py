import gi
import logging
import sys
from time import sleep
from threading import Thread

gi.require_version("Gtk", "3.0")
from fapolicy_analyzer import (
    Handle,
    is_fapolicyd_active,
    start_fapolicyd,
    stop_fapolicyd,
)

from fapolicy_analyzer.ui.actions import (
    REQUEST_DAEMON_START,
    REQUEST_DAEMON_STOP,
    REQUEST_DAEMON_RELOAD,
    REQUEST_DAEMON_STATUS,
    REQUEST_DAEMON_STATUS_UPDATE,
    daemon_initialized,
    error_daemon_reload,
    error_daemon_start,
    error_daemon_status,
    error_daemon_stop,
    init_daemon,
    received_daemon_reload,
    received_daemon_start,
    received_daemon_status,
    received_daemon_status_update,
    request_daemon_status_update,
    received_daemon_stop,
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
_fapd_status: bool
_fapd_ref: Handle


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
                GLib.idle_add(finish, daemon)
            except RuntimeError:
                logging.exception(DAEMON_INITIALIZATION_ERROR)
                GLib.idle_add(sys.exit, 1)

        def monitor_daemon(timeout=5):
            while True:
                # GLib.idle_add(update_fapd_status, is_fapolicyd_active())
                logging.debug("monitor_daemon(): Dispatching update request")
                dispatch(request_daemon_status_update())
                sleep(timeout)

        def start_daemon_monitor():
            logging.debug("start_daemon_monitor()")
            thread = Thread(target=monitor_daemon)
            thread.daemon = True
            thread.start()
            # dispatch(received_daemon_status_update(is_fapolicyd_active()))

        def finish(daemon: Handle):
            global _fapd_ref, _fapd_status
            _fapd_ref = daemon
            _fapd_status = is_fapolicyd_active()
            dispatch(daemon_initialized())

        if daemon:
            finish(daemon)
        else:
            acquire_daemon()
            start_daemon_monitor()
        return init_daemon()

    def _daemon_reload(action: Action) -> Action:
        logging.debug("_daemon_reload(action: Action) -> Action")
        return received_daemon_reload()

    def _daemon_start(action: Action) -> Action:
        logging.debug("_daemon_start(action: Action) -> Action")
        start_fapolicyd()
        return received_daemon_start()

    def _daemon_status(action: Action) -> Action:
        logging.debug(f"_daemon_status(action: {action}) -> Action")
        status = is_fapolicyd_active()
        logging.debug(f"_daemon_status::Fapolicyd status: {status}")
        _fapd_status = status
        return received_daemon_status(_fapd_status)

    def _daemon_status_update(action: Action) -> Action:
        logging.debug(f"_daemon_status_update(action: {action})")
        status = is_fapolicyd_active()
        logging.debug(f"_daemon_status_update::Fapolicyd status: {status}")
        _fapd_status = status
        return received_daemon_status_update(_fapd_status)

    def _daemon_stop(action: Action) -> Action:
        logging.debug("_daemon_stop(action: Action) -> Action")
        stop_fapolicyd()
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

    request_daemon_status_epic = pipe(
        of_type(REQUEST_DAEMON_STATUS),
        map(_daemon_status),
        catch(lambda ex, source: of(error_daemon_status(str(ex)))),
    )

    request_daemon_status_update_epic = pipe(
        of_type(REQUEST_DAEMON_STATUS_UPDATE),
        map(_daemon_status_update),
        catch(lambda ex, source: of(error_daemon_status(str(ex)))),
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
        request_daemon_status_epic,
        request_daemon_status_update_epic,
        request_daemon_stop_epic,
    )

    return create_feature_module(DAEMON_FEATURE,
                                 daemon_reducer,
                                 epic=daemon_epic,
                                 )
