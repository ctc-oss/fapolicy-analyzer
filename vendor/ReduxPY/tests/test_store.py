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
import unittest
from unittest import TestCase
from os.path import dirname
from redux import create_store, create_action, select_feature, ReduxRootStore, select
from rx.operators import map, first, filter
from rx.subject import Subject
from rx import Observable
from rx.core.typing import Observer
from .init.feature import create_init_feature, select_init_feature_module

# Current directory
HERE = dirname(__file__)


def raise_error(error):
    raise error


class TestReduxStore(TestCase):
    def test_type(self):
        store = create_store()

        self.assertIsInstance(store, ReduxRootStore)

        store.on_completed()

    def test_store(self):
        store = create_store()

        store_ = store.as_observable()

        init_state_ = store_.pipe(
            select(select_init_feature_module), filter(bool), first()
        )

        test_ = init_state_.pipe(
            map(lambda state: self.assertEqual(state, "init")), first(),
        )

        store.add_feature_module(create_init_feature())

        test_.subscribe()

        store.on_completed()


if __name__ == "__main__":
    unittest.main()
