from redux import Action, Reducer, handle_actions
from typing import Sequence, cast
from fapolicy_analyzer.ui.actions import (
    ADD_NOTIFICATION,
    Notification,
    REMOVE_NOTIFICATION,
)


def handle_add_notification(
    state: Sequence[Notification], action: Action
) -> Sequence[Notification]:
    payload = cast(Notification, action.payload)
    return (*state, payload)


def handle_remove_notification(
    state: Sequence[Notification], action: Action
) -> Sequence[Notification]:
    payload = cast(Notification, action.payload)
    return [n for n in state if n.id != payload.id]


notification_reducer: Reducer = handle_actions(
    {
        ADD_NOTIFICATION: handle_add_notification,
        REMOVE_NOTIFICATION: handle_remove_notification,
    },
    [],
)
