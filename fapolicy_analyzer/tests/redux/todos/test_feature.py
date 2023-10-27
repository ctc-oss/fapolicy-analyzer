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

from .feature import create_todos_feature, select_todos_feature
from .action import add_todo
from unittest.case import TestCase
from rx.operators import last
from rx.subject import BehaviorSubject

from fapolicy_analyzer.redux import create_store


class TestTodoReducer(TestCase):
    def test_add_todo(self):
        store = create_store()

        store.add_feature_module(create_todos_feature())

        result = BehaviorSubject(None)

        store.as_observable().pipe(last()).subscribe(result)

        store.dispatch(add_todo("new todo"))
        store.dispatch(add_todo("another todo"))
        store.on_completed()

        feat = select_todos_feature(result.value)

        assert len(feat["todos"]) == 2
