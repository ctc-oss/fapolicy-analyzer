import context  # noqa: F401
from unittest.mock import MagicMock
from ui.actions import Notification, NotificationType
from ui.reducers.notification_reducer import (
    handle_add_notification,
    handle_remove_notification,
)


def test_handle_add_notification():
    result = handle_add_notification([], MagicMock(payload="foo"))
    assert list(result) == ["foo"]


def test_handle_remove_notification():
    state = [
        Notification(id=99, text=None, type=NotificationType.ERROR),
        Notification(id=100, text=None, type=NotificationType.ERROR),
    ]
    result = handle_remove_notification(
        state, MagicMock(payload=Notification(id=99, text=None, type=None))
    )
    assert result == state[1:]
