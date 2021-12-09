import pytest
from unittest.mock import MagicMock
from ui.reducers.daemon_reducer import (
    handle_received_daemon_start,
    # handle_received_daemon_stop,
    # handle_received_daemon_reload,
    # handle_received_daemon_status,
    # handle_received_daemon_status_update,
)

from ui.actions import DaemonState


@pytest.fixture
def initial_state():
    return DaemonState(error=None, status=False, handle=None)


def test_handle_received_daemon_start(initial_state):
    mockDaemon = MagicMock()
    ret = handle_received_daemon_start(initial_state, mockDaemon)
    print(ret)
    assert ret != DaemonState(error=None, status=False, handle=mockDaemon)


def test_handle_received_daemon_stop():
    pass


def test_handle_received_daemon_reload():
    pass


def test_handle_received_daemon_status():
    pass


def test_handle_received_daemon_status_update():
    pass
