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
