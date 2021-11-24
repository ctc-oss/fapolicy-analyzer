from fapolicy_analyzer.ui.actions import (
    ERROR_USERS,
    RECEIVED_USERS,
    REQUEST_USERS,
)
from fapolicy_analyzer import User
from fapolicy_analyzer.redux import Action, Reducer, handle_actions
from typing import Any, NamedTuple, Optional, Sequence, cast


class UserState(NamedTuple):
    error: str
    loading: bool
    users: Sequence[User]


def _create_state(state: UserState, **kwargs: Optional[Any]) -> UserState:
    return UserState(**{**state._asdict(), **kwargs})


def handle_request_users(state: UserState, action: Action) -> UserState:
    return _create_state(state, loading=True, error=None)


def handle_received_users(state: UserState, action: Action) -> UserState:
    payload = cast(Sequence[User], action.payload)
    return _create_state(state, users=payload, error=None, loading=False)


def handle_error_users(state: UserState, action: Action) -> UserState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload, loading=False)


user_reducer: Reducer = handle_actions(
    {
        REQUEST_USERS: handle_request_users,
        RECEIVED_USERS: handle_received_users,
        ERROR_USERS: handle_error_users,
    },
    UserState(error=None, users=[], loading=False),
)
