# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
#
#
# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# CTC License # CTC License # CTC License # CTC License # CTC License # CTC
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
