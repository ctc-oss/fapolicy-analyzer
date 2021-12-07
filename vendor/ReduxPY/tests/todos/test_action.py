from unittest.case import TestCase

from .action import (
    ACTION_ADD_TODO,
    ACTION_SET_VISIBILITY_FILTER,
    ACTION_TOGGLE_TODO,
    VisibilityFilters,
    add_todo,
    set_visibility_filter,
    toggle_todo,
)


class TestAction(TestCase):

    def test_add_todo(self):

        text = 'My Action'

        action = add_todo(text)
        assert action.type == ACTION_ADD_TODO
        assert action.payload.text == text

    def test_visibility_filter(self):

        fltr = VisibilityFilters.SHOW_ALL

        action = set_visibility_filter(fltr)
        assert action.type == ACTION_SET_VISIBILITY_FILTER
        assert action.payload == fltr

    def test_toggle_todo(self):

        item_id = 10

        action = toggle_todo(item_id)
        assert action.type == ACTION_TOGGLE_TODO
        assert action.payload == item_id
