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
