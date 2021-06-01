import context  # noqa: F401
import pytest
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from time import sleep
from ui.notification import Notification
from ui.state_manager import stateManager, NotificationType


@pytest.fixture
def widget():
    widget = Notification(1)
    overlay = Gtk.Overlay()
    overlay.add_overlay(widget.get_content())
    parent = Gtk.Window()
    parent.add(overlay)
    return widget


@pytest.fixture
def state():
    yield stateManager
    stateManager.systemNotification = None


@pytest.mark.parametrize("notification_type", list(NotificationType))
def test_shows_notification(widget, state, notification_type):
    state.add_system_notification("foo", notification_type)
    assert widget.get_content().get_child_revealed()
    assert widget.builder.get_object("message").get_label() == "foo"
    assert (
        widget.builder.get_object("container")
        .get_style_context()
        .has_class(notification_type.name.lower())
    )


@pytest.mark.parametrize("notification_type", list(NotificationType))
def test_closes_notification(widget, state, notification_type):
    state.add_system_notification("foo", notification_type)
    assert widget.get_content().get_child_revealed()
    widget.builder.get_object("closeBtn").clicked()
    assert not widget.get_content().get_child_revealed()


@pytest.mark.parametrize(
    "notification_type", [NotificationType.SUCCESS, NotificationType.INFO]
)
def test_notification_times_out(widget, state, notification_type):
    state.add_system_notification("foo", notification_type)
    assert widget.get_content().get_child_revealed()
    sleep(1.2)
    assert not widget.get_content().get_child_revealed()


@pytest.mark.parametrize(
    "notification_type", [NotificationType.ERROR, NotificationType.WARN]
)
def test_notification_does_not_time_out(widget, state, notification_type):
    state.add_system_notification("foo", notification_type)
    assert widget.get_content().get_child_revealed()
    sleep(1.2)
    assert widget.get_content().get_child_revealed()
