"""
    Implements feature specific functions
"""

from functools import partial
from logging import getLogger
from typing import Any, Callable, Iterable, Optional

import rx.operators as op
from rx import Observable, pipe
from rx.core.typing import Mapper, Predicate

from .action import is_by_selector, is_type, select_action_payload
from .constants import INIT_ACTION
from .types import (Action, Epic, Reducer, ReduxFeatureModule, ReduxRootState,
                    StateType)

logger = getLogger(__name__)


def has_payload(payload: Any) -> Predicate[Action]:
    """ Returns a function that checks if the action has a particular payload

        Args:
            payload: payload to test against

        Returns:
            Function to execute the check against an action
    """

    return is_by_selector(payload, select_action_payload)


def of_init_feature(
        identifier: str) -> Mapper[Observable, Observable]:
    """ Operator to test for the initialization action of a feature

        Args:
            identifier: the identifier of the feature

        Returns:
            Operator function that accepts init actions for the feature, once

    """
    return pipe(
        op.filter(is_type(INIT_ACTION)),
        op.filter(has_payload(identifier)),
        op.take(1),
        op.map(lambda x: identifier),
        op.do_action(logger.debug)
    )


def create_feature_module(
    identifier: str,
    reducer: Optional[Reducer] = None,
    epic: Optional[Epic] = None,
    dependencies: Iterable[ReduxFeatureModule] = (),
) -> ReduxFeatureModule:
    """ Constructs a new feature module descriptor

        Args:
            identifier: the identifier of the feature
            reducer: optional reducer
            epic: optional epic
            dependencies: optional dependencies on other features

        Returns:
            The feature module descriptor

    """
    return ReduxFeatureModule(identifier, reducer, epic, dependencies)


def _select_feature_by_id(
        identifier: str,
        initial_state: Optional[StateType],
        state: ReduxRootState) -> Optional[StateType]:
    """ Selector function that selects the feature state from the root state"""
    return state.get(identifier, initial_state)


def select_feature(
    identifier: str, initial_state: Optional[StateType] = None
) -> Callable[[ReduxRootState], Optional[StateType]]:
    """ Returns a function that returns the feature state from the root state

        Args:
            identifier: identifier of the feature
            initial_state: fallback state used if the feature state is not defined

        Returns:
            The selector function

    """
    return partial(_select_feature_by_id, identifier, initial_state)
