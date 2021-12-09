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
