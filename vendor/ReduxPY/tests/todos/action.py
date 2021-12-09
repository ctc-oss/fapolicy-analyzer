""" Action objects and constants """
from enum import Enum
from itertools import count
from typing import Callable, Iterable, Iterator, NamedTuple

from redux import Action, create_action

from .constants import FEATURE_NAME

ACTION_ADD_TODO = '%s Add Todo' % FEATURE_NAME
ACTION_TOGGLE_TODO = '%s Toggle Todo' % FEATURE_NAME
ACTION_SET_VISIBILITY_FILTER = '%s Set Visibility Filter' % FEATURE_NAME


class VisibilityFilters(Enum):
    SHOW_ALL = 'SHOW_ALL'
    SHOW_COMPLETED = 'SHOW_COMPLETED'
    SHOW_ACTIVE = 'SHOW_ACTIVE'


class TodoPayload(NamedTuple):
    """ Todo payload """
    id: int
    text: str


_add_todo = create_action(ACTION_ADD_TODO)
_ids: Iterator[int] = iter(count())


# pylint: disable=unsubscriptable-object
def add_todo(text: str) -> Action:
    return _add_todo(TodoPayload(next(_ids), text))


# pylint: disable=unsubscriptable-object
set_visibility_filter: Callable[[VisibilityFilters], Action] = create_action(
    ACTION_SET_VISIBILITY_FILTER)

# pylint: disable=unsubscriptable-object
toggle_todo: Callable[[int], Action] = create_action(
    ACTION_TOGGLE_TODO)
