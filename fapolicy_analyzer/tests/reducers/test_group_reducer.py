import context  # noqa: F401
import pytest
from unittest.mock import MagicMock
from ui.reducers.group_reducer import (
    GroupState,
    handle_error_groups,
    handle_received_groups,
)


@pytest.fixture()
def initial_state():
    return GroupState(error=None, groups=[])


def test_handle_received_groups(initial_state):
    result = handle_received_groups(initial_state, MagicMock(payload=["foo"]))
    assert result == GroupState(error=None, groups=["foo"])


def test_handle_error_groups(initial_state):
    result = handle_error_groups(initial_state, MagicMock(payload="foo"))
    assert result == GroupState(error="foo", groups=[])
