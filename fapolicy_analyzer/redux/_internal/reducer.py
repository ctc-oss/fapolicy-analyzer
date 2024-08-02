# Copyright 2021 Dr. Carsten Leue
# Copyright Concurrent Technologies Corporation 2021
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
    Implements reducer related function
"""

from functools import partial
from typing import Iterable, Mapping, MutableMapping, Optional, Tuple

from .action import select_action_type
from .types import Action, Reducer, StateType


def _default_reducer(
    initial_state: Optional[StateType], state: StateType, _: Action
) -> Optional[StateType]:
    #: default handling
    return state if state else initial_state


def default_reducer(initial_state: Optional[StateType]) -> Reducer:
    """Creates a reducer that returns the original state or the default state.

    Args:
        inital_state: optional initial state used as a fallback

    Returns:
        A reducer that reduces the current state or the initial state as a fallback

    """
    return partial(_default_reducer, initial_state)


def _handle_actions_reducer(
    action_map: Mapping[str, Reducer],
    def_reducer: Reducer,
    state: StateType,
    action: Action,
) -> Optional[StateType]:
    #: dispatch
    return action_map.get(select_action_type(action), def_reducer)(state, action)


def handle_actions(
    action_map: Mapping[str, Reducer],
    initial_state: Optional[StateType] = None,
) -> Reducer:
    """Creates a new reducer from a mapping of action name to reducer for that action.

    Args:
        action_map: mapping from action name to reducer for that action
        initial_state: optional initial state used if no reducer matches

    Returns:
        A reducer function that handles the actions in the map

    """
    return partial(
        _handle_actions_reducer, {**action_map}, default_reducer(initial_state)
    )


def _combine_reducers(
    items: Iterable[Tuple[str, Reducer]], state: Mapping[str, StateType], action: Action
) -> Mapping[str, StateType]:
    """Updates the state object from the reducer mappings."""
    result = state if state else {}
    mutable: Optional[MutableMapping[str, StateType]] = None
    for key, value in items:
        current = result.get(key)
        updated = value(current, action)
        if current is not updated:
            if not mutable:
                mutable = dict(result)
                result = mutable
            mutable[key] = updated
    return result


def combine_reducers(
    reducers: Mapping[str, Reducer],
) -> Reducer[Mapping[str, StateType]]:
    """Creates a new reducer from a mapping of reducers.

    Args:
        reducers: the mapping from state partition to reducer

    Returns:
        A reducer that dispatches actions against each of the mapped reducers

    """
    return partial(_combine_reducers, tuple(reducers.items()))
