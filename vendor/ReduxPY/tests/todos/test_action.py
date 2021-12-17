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
