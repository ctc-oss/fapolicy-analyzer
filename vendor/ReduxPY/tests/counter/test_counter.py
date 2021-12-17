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
from typing import Iterable, MutableMapping, MutableSequence, Optional, Sequence
from unittest.case import TestCase

from rx import Observable, operators
from rx.subject import BehaviorSubject
from rx.testing import ReactiveTest, TestScheduler

from redux import ReduxRootStore, create_store, select

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
