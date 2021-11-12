import context  # noqa: F401
import pytest
from unittest.mock import MagicMock
from ui.reducers.user_reducer import (
    UserState,
    handle_error_users,
    handle_received_users,
)


@pytest.fixture()
def initial_state():
    return UserState(error=None, users=[])


def test_handle_received_users(initial_state):
    result = handle_received_users(initial_state, MagicMock(payload=["foo"]))
    assert result == UserState(error=None, users=["foo"])


def test_handle_error_users(initial_state):
    result = handle_error_users(initial_state, MagicMock(payload="foo"))
    assert result == UserState(error="foo", users=[])
