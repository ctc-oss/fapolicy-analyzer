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

""" Action objects and constants """
from enum import Enum
from itertools import count
from typing import Callable, Iterator, NamedTuple

from fapolicy_analyzer.redux import Action, create_action

from .constants import FEATURE_NAME

ACTION_ADD_TODO = "%s Add Todo" % FEATURE_NAME
ACTION_TOGGLE_TODO = "%s Toggle Todo" % FEATURE_NAME
ACTION_SET_VISIBILITY_FILTER = "%s Set Visibility Filter" % FEATURE_NAME


class VisibilityFilters(Enum):
    SHOW_ALL = "SHOW_ALL"
    SHOW_COMPLETED = "SHOW_COMPLETED"
    SHOW_ACTIVE = "SHOW_ACTIVE"


class TodoPayload(NamedTuple):
    """Todo payload"""

    id: int
    text: str


_add_todo = create_action(ACTION_ADD_TODO)
_ids: Iterator[int] = iter(count())


# pylint: disable=unsubscriptable-object
def add_todo(text: str) -> Action:
    return _add_todo(TodoPayload(next(_ids), text))


# pylint: disable=unsubscriptable-object
set_visibility_filter: Callable[[VisibilityFilters], Action] = create_action(
    ACTION_SET_VISIBILITY_FILTER
)

# pylint: disable=unsubscriptable-object
toggle_todo: Callable[[int], Action] = create_action(ACTION_TOGGLE_TODO)
