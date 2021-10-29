import context  # noqa: F401
import pytest
from unittest.mock import MagicMock
from ui.reducers.event_reducer import (
    EventState,
    handle_error_events,
    handle_received_events,
)


@pytest.fixture()
def initial_state():
    return EventState(error=None, events=[])


def test_handle_received_events(initial_state):
    result = handle_received_events(initial_state, MagicMock(payload=["foo"]))
    assert result == EventState(error=None, events=["foo"])


def test_handle_error_events(initial_state):
    result = handle_error_events(initial_state, MagicMock(payload="foo"))
    assert result == EventState(error="foo", events=[])
