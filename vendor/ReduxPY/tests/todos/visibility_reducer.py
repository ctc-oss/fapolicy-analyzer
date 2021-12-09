from typing import cast

from redux import Action, Reducer, create_action, handle_actions

from .action import ACTION_SET_VISIBILITY_FILTER, VisibilityFilters


def handle_visibility_filter(state: VisibilityFilters,
                             action: Action) -> VisibilityFilters:
    payload = cast(VisibilityFilters, action.payload)
    print('payload', payload)
    return payload


visibility_filter: Reducer = handle_actions(
    {ACTION_SET_VISIBILITY_FILTER: handle_visibility_filter}, VisibilityFilters.SHOW_ALL)
