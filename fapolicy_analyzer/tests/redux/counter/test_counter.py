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

from typing import Iterable
from unittest.case import TestCase

from rx import Observable, operators
from rx.subject import BehaviorSubject

from fapolicy_analyzer.redux import ReduxRootStore, create_store

from .action import DECREMENT_ACTION, INCREMENT_ACTION
from .feature import create_counter_feature, select_counter_feature


class TestCounter(TestCase):

    def test_type(self):

        def reduce_to_list(dst: Iterable[int], src: int) -> Iterable:
            return (*dst, src)

        store = create_store()
        store.add_feature_module(create_counter_feature())

        result = BehaviorSubject(None)

        store_: Observable[ReduxRootStore] = store.as_observable()
        store_.pipe(
            operators.map(select_counter_feature),
            operators.reduce(reduce_to_list, ()),
            operators.first()
        ).subscribe(result)

        store.dispatch(INCREMENT_ACTION)
        store.dispatch(DECREMENT_ACTION)

        store.on_completed()

        assert result.value == (0, 1, 0)
