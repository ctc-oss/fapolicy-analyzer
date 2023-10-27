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

from fapolicy_analyzer.redux import Action

from .action import add_todo, toggle_todo
from .todo_reducer import todos


class TestTodoReducer(TestCase):
    def test_initial_state(self):
        result = todos(None, Action("sample", None))
        assert result == ()

    def test_add_todo(self):
        r1 = todos((), add_todo("todo1"))
        assert len(r1) == 1

        r2 = todos(r1, add_todo("todo2"))
        assert len(r1) == 1
        assert len(r2) == 2

    def test_toggle_todo(self):
        r1 = todos((), add_todo("todo1"))
        r2 = todos(r1, add_todo("todo2"))

        idx = len(r2) - 1
        id2 = r2[idx].id

        r3 = todos(r2, toggle_todo(id2))

        assert r3[idx].id == id2
        assert r3[idx].completed is True

        assert r2[idx].id == id2
        assert r2[idx].completed is False
