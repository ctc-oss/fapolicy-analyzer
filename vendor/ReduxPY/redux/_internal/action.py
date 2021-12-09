"""
    Implements action specific functions
"""

from functools import partial
from typing import Any

import rx.operators as op
from rx import Observable
from rx.core.typing import Mapper, Predicate

from .types import Action, PayloadType


def create_action(type_name: str) -> Mapper[PayloadType, Action]:
    """ Creates a function that produces an action of the given type

        Args:
            type_name: type of the action

        Returns:
            A function that accepts the action payload and creates the action
    """
    return partial(Action, type_name)


def select_action_type(action: Action) -> str:
    """ Selects the type from the action

        Args:
            action: the action object

        Returns:
            the type of the action
    """
    return action.type


def select_action_payload(action: Action) -> PayloadType:
    """ Selects the payload from the action

        Args:
            action: the action object

        Returns:
            the payload of the action
    """
    return action.payload


def _is_by_selector(value: Any, selector: Mapper[Action, Any], action: Action) -> bool:
    """ Checks if selector on an action matches a value

        Args:
            action: the action object

        Returns:
            true if the selector result of the action matches, else false

    """

    return selector(action) is value


def is_by_selector(
    value: Any, selector: Mapper[Action, Any]
) -> Predicate[Action]:
    """ Returns a function that checks if the selector on an action equals a particular value

        Args:
            value: the value to compare against
            selector: the selector to use to extract the value from the action

        Returns:
            Function to execute the check against an action
    """
    return partial(_is_by_selector, value, selector)


def is_type(type_name) -> Predicate[Action]:
    """ Returns a function that checks if the action is of a particular type

        Args:
            type_name: type of the action to check for

        Returns:
            Function to execute the check against an action
    """

    return is_by_selector(type_name, select_action_type)


def of_type(
        type_name: str) -> Mapper[Observable, Observable]:
    """ Returns a reactive operator that filters for actions of the given type

        Args:
            type_name: type of the action to filter for

        Returns:
            The filter operator function
    """
    return op.filter(is_type(type_name))
