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
