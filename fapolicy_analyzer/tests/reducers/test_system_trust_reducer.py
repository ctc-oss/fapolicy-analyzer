import context  # noqa: F401
import pytest
from unittest.mock import MagicMock
from ui.reducers.system_trust_reducer import (
    TrustState,
    handle_error_system_trust,
    handle_received_system_trust,
    handle_request_system_trust,
)


@pytest.fixture()
def initial_state():
    return TrustState(error=None, trust=[], loading=False)


def test_handle_request_system_trust(initial_state):
    result = handle_request_system_trust(initial_state, MagicMock())
    assert result == TrustState(error=None, trust=[], loading=True)


def test_handle_received_system_trust(initial_state):
    result = handle_received_system_trust(initial_state, MagicMock(payload=["foo"]))
    assert result == TrustState(error=None, trust=["foo"], loading=False)


def test_handle_error_system_trust(initial_state):
    result = handle_error_system_trust(initial_state, MagicMock(payload="foo"))
    assert result == TrustState(error="foo", trust=[], loading=False)
