import logging
from fapolicy_analyzer import System
from redux import Action, create_store
from redux import select_feature
from rx import operators
from rx.core.typing import Observable
from .features import (
    NOTIFICATIONS_FEATURE,
    SYSTEM_FEATURE,
    DAEMON_FEATURE,
    create_notification_feature,
    create_system_feature,
    create_daemon_feature,
)


store = create_store()


def init_store(system: System = None, daemon=None):
    """
    Initializes the Redux store.

    Keyword arguments:
    system -- the fapolicy_analyzer.System object, defaults to None. If not provided,
              a new System object will be initialized.  Used for testing purposes only.
    """
    logging.debug(f"store.init_store(system={system}, daemon={daemon})")
    store.add_feature_module(create_notification_feature())
    store.add_feature_module(create_system_feature(store.dispatch, system))
    store.add_feature_module(create_daemon_feature(store.dispatch, daemon))


def dispatch(action: Action) -> None:
    store.dispatch(action)


def get_notifications_feature() -> Observable:
    return store.as_observable().pipe(
        operators.map(select_feature(NOTIFICATIONS_FEATURE))
    )


def get_system_feature() -> Observable:
    return store.as_observable().pipe(
        operators.map(select_feature(SYSTEM_FEATURE)))


def get_daemon_feature() -> Observable:
    return store.as_observable().pipe(
        operators.map(select_feature(DAEMON_FEATURE)))
