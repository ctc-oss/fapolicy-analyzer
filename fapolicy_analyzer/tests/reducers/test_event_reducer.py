import context  # noqa: F401
import pytest
from unittest.mock import MagicMock
from ui.reducers.event_reducer import (
    EventState,
    handle_error_events,
    handle_received_events,
    handle_request_events,
)


@pytest.fixture()
def initial_state():
    return EventState(error=None, log=[], loading=False)


def test_handle_request_events(initial_state):
    result = handle_request_events(initial_state, MagicMock())
    assert result == EventState(error=None, log=[], loading=True)


def test_handle_received_events(initial_state):
    result = handle_received_events(initial_state, MagicMock(payload=["foo"]))
    assert result == EventState(error=None, log=["foo"], loading=False)


def test_handle_error_events(initial_state):
    result = handle_error_events(initial_state, MagicMock(payload="foo"))
    assert result == EventState(error="foo", log=[], loading=False)
