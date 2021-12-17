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
from .feature import create_todos_feature, select_todos_feature
from .action import add_todo
from unittest.case import TestCase
from rx.operators import last
from rx.subject import BehaviorSubject

from redux import create_store


class TestTodoReducer(TestCase):

    def test_add_todo(self):

        store = create_store()

        store.add_feature_module(create_todos_feature())

        result = BehaviorSubject(None)

        store.as_observable().pipe(last()).subscribe(result)

        store.dispatch(add_todo('new todo'))
        store.dispatch(add_todo('another todo'))
        store.on_completed()

        feat = select_todos_feature(result.value)

        assert len(feat['todos']) == 2
