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
        text = "My Action"

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
