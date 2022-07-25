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

from typing import Sequence, cast

from fapolicy_analyzer.redux import Action, Reducer, handle_actions

from .action import ACTION_ADD_TODO, ACTION_TOGGLE_TODO, TodoPayload
from .state import TodoItem


def handle_add_todo(state: Sequence[TodoItem],
                    action: Action) -> Sequence[TodoItem]:
    payload = cast(TodoPayload, action.payload)
    return (*state, TodoItem(payload.id, payload.text, False))


def handle_toggle_todo(
        state: Sequence[TodoItem], action: Action) -> Sequence[TodoItem]:

    key = cast(int, action.payload)

    return [TodoItem(item.id, item.text, not item.completed)
            if item.id == key else item for item in state]


todos: Reducer = handle_actions(
    {ACTION_ADD_TODO: handle_add_todo, ACTION_TOGGLE_TODO: handle_toggle_todo}, ())
