import context  # noqa: F401
import pytest
from unittest.mock import MagicMock
from ui.reducers.ancillary_trust_reducer import (
    TrustState,
    handle_add_changesets,
    handle_ancillary_trust_deployed,
    handle_clear_changesets,
    handle_error_ancillary_trust,
    handle_error_deploying_ancillary_trust,
    handle_received_ancillary_trust,
)


@pytest.fixture()
def initial_state():
    return TrustState(error=None, trust=[], deployed=False)


def test_handle_received_ancillary_trust(initial_state):
    result = handle_received_ancillary_trust(initial_state, MagicMock(payload=["foo"]))
    assert result == TrustState(error=None, trust=["foo"], deployed=False)


def test_handle_error_ancillary_trust(initial_state):
    result = handle_error_ancillary_trust(initial_state, MagicMock(payload="foo"))
    assert result == TrustState(error="foo", trust=[], deployed=False)


def test_handle_ancillary_trust_deployed(initial_state):
    result = handle_ancillary_trust_deployed(initial_state, MagicMock())
    assert result == TrustState(error=None, trust=[], deployed=True)


def test_handle_error_deploying_ancillary_trust(initial_state):
    result = handle_error_deploying_ancillary_trust(
        initial_state, MagicMock(payload="foo")
    )
    assert result == TrustState(error="foo", trust=[], deployed=False)


def test_handle_add_changesets(initial_state):
    result = handle_add_changesets(initial_state, MagicMock())
    assert result == TrustState(error=None, trust=[], deployed=False)


def test_handle_clear_changesets(initial_state):
    result = handle_clear_changesets(initial_state, MagicMock())
    assert result == TrustState(error=None, trust=[], deployed=True)
