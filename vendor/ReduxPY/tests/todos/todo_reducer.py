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
from typing import Sequence, cast

from redux import Action, Reducer, handle_actions

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
