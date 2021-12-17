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

from redux import Action

from .action import add_todo, toggle_todo
from .todo_reducer import todos


class TestTodoReducer(TestCase):

    def test_initial_state(self):
        result = todos(None, Action('sample', None))
        assert result == ()

    def test_add_todo(self):

        r1 = todos((), add_todo('todo1'))
        assert len(r1) == 1

        r2 = todos(r1, add_todo('todo2'))
        assert len(r1) == 1
        assert len(r2) == 2

    def test_toggle_todo(self):
        r1 = todos((), add_todo('todo1'))
        r2 = todos(r1, add_todo('todo2'))

        idx = len(r2) - 1
        id2 = r2[idx].id

        r3 = todos(r2, toggle_todo(id2))

        assert r3[idx].id == id2
        assert r3[idx].completed == True

        assert r2[idx].id == id2
        assert r2[idx].completed == False
