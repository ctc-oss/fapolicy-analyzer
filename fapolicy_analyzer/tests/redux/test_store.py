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

import unittest
from unittest import TestCase
from os.path import dirname
from fapolicy_analyzer.redux import create_store, create_action, select_feature, ReduxRootStore, select
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
