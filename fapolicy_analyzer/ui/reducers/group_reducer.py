from fapolicy_analyzer.ui.actions import ERROR_GROUPS, RECEIVED_GROUPS, REQUEST_GROUPS
from fapolicy_analyzer import Group
from redux import Action, Reducer, handle_actions
from typing import Any, NamedTuple, Optional, Sequence, cast


class GroupState(NamedTuple):
    error: str
    loading: bool
    groups: Sequence[Group]


def _create_state(state: GroupState, **kwargs: Optional[Any]) -> GroupState:
    return GroupState(**{**state._asdict(), **kwargs})


def handle_request_groups(state: GroupState, action: Action) -> GroupState:
    return _create_state(state, loading=True, error=None)


def handle_received_groups(state: GroupState, action: Action) -> GroupState:
    payload = cast(Sequence[Group], action.payload)
    return _create_state(state, groups=payload, error=None, loading=False)


def handle_error_groups(state: GroupState, action: Action) -> GroupState:
    payload = cast(str, action.payload)
    return _create_state(state, error=payload, loading=False)


group_reducer: Reducer = handle_actions(
    {
        REQUEST_GROUPS: handle_request_groups,
        RECEIVED_GROUPS: handle_received_groups,
        ERROR_GROUPS: handle_error_groups,
    },
    GroupState(error=None, groups=[], loading=False),
)
