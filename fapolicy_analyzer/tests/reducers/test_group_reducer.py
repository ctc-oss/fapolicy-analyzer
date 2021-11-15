import context  # noqa: F401
import pytest
from unittest.mock import MagicMock
from ui.reducers.group_reducer import (
    GroupState,
    handle_error_groups,
    handle_received_groups,
    handle_request_groups,
)


@pytest.fixture()
def initial_state():
    return GroupState(error=None, groups=[], loading=False)


def test_handle_request_groups(initial_state):
    result = handle_request_groups(initial_state, MagicMock())
    assert result == GroupState(error=None, groups=[], loading=True)


def test_handle_received_groups(initial_state):
    result = handle_received_groups(initial_state, MagicMock(payload=["foo"]))
    assert result == GroupState(error=None, groups=["foo"], loading=False)


def test_handle_error_groups(initial_state):
    result = handle_error_groups(initial_state, MagicMock(payload="foo"))
    assert result == GroupState(error="foo", groups=[], loading=False)
