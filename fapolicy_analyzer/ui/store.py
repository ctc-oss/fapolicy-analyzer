from redux import Action, create_feature_module, create_store
from redux import select_feature
from rx import operators
from rx.core.typing import Observable
from .epics import system_epic
from .reducers import notification_reducer, system_reducer

NOTIFICATIONS_FEATURE = "notifications"
SYSTEM_FEATURE = "system"

store = create_store()
store.add_feature_module(
    create_feature_module(NOTIFICATIONS_FEATURE, notification_reducer)
)
store.add_feature_module(
    create_feature_module(SYSTEM_FEATURE, system_reducer, epic=system_epic)
)


def dispatch(action: Action) -> None:
    store.dispatch(action)


def get_notifications_feature() -> Observable:
    return store.as_observable().pipe(
        operators.map(select_feature(NOTIFICATIONS_FEATURE))
    )


def get_system_feature() -> Observable:
    return store.as_observable().pipe(operators.map(select_feature(SYSTEM_FEATURE)))
