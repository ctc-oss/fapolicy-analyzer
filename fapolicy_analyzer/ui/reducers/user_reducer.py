from fapolicy_analyzer.ui.actions import (
    ERROR_USERS,
    RECEIVED_USERS,
)
from fapolicy_analyzer import User
from redux import Action, Reducer, handle_actions
from typing import Any, NamedTuple, Optional, Sequence, cast


class UserState(NamedTuple):
    error: str
    users: Sequence[User]


def _create_state(state: UserState, **kwargs: Optional[Any]) -> UserState:
    return UserState(**{**state._asdict(), **kwargs})


def handle_received_users(state: UserState, action: Action) -> UserState:
    payload = cast(Sequence[User], action.payload)
    return _create_state(state, users=payload, error=None)


def handle_error_users(state: UserState, action: Action) -> UserState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload)


user_reducer: Reducer = handle_actions(
    {
        RECEIVED_USERS: handle_received_users,
        ERROR_USERS: handle_error_users,
    },
    UserState(error=None, users=[]),
)
