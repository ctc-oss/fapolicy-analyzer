# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import context  # noqa: F401 # isort: skip
from time import sleep

import gi
import pytest
from callee import Attrs, InstanceOf
from rx.subject import Subject

from fapolicy_analyzer.redux import Action
from fapolicy_analyzer.ui.actions import REMOVE_NOTIFICATION
from fapolicy_analyzer.ui.actions import Notification as Note
from fapolicy_analyzer.ui.actions import NotificationType
from fapolicy_analyzer.ui.notification import Notification
from fapolicy_analyzer.ui.session_manager import sessionManager

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("fapolicy_analyzer.ui.notification.dispatch")


@pytest.fixture
def mock_notifications_feature(mocker):
    notifications_feature_mock = Subject()
    mocker.patch(
        "fapolicy_analyzer.ui.notification.get_notifications_feature",
        return_value=notifications_feature_mock,
    )
    yield notifications_feature_mock
    notifications_feature_mock.on_completed()


@pytest.fixture
def widget(mock_notifications_feature, notifications):
    widget = Notification(1)
    overlay = Gtk.Overlay()
    overlay.add_overlay(widget.get_ref())
    parent = Gtk.Window()
    parent.add(overlay)
    mock_notifications_feature.on_next(notifications)
    return widget


@pytest.fixture
def state():
    yield sessionManager
    sessionManager.systemNotification = None


@pytest.mark.usefixtures("mock_notifications_feature")
@pytest.mark.parametrize(
    "notifications, notification_type",
    [([Note(0, "foo", t, None)], t) for t in list(NotificationType)],
)
def test_shows_notification(widget, notification_type):
    assert widget.get_ref().get_child_revealed()
    assert widget.get_object("message").get_label() == "foo"
    assert (
        widget.get_object("container")
        .get_style_context()
        .has_class(notification_type.name.lower())
    )


@pytest.mark.usefixtures("mock_notifications_feature")
@pytest.mark.parametrize(
    "notifications",
    [[Note(0, "foo", t, None)] for t in list(NotificationType)],
)
def test_closes_notification(widget, mock_dispatch, mock_notifications_feature):
    assert widget.get_ref().get_child_revealed()
    widget.get_object("closeBtn").clicked()
    mock_dispatch.assert_called()

    # since we are mocking dispatch we have to manually fire the on_next
    mock_notifications_feature.on_next([])
    assert not widget.get_ref().get_child_revealed()


@pytest.mark.usefixtures("mock_notifications_feature")
@pytest.mark.parametrize(
    "notifications",
    [
        [Note(0, "foo", t, None)]
        for t in [
            NotificationType.SUCCESS,
            NotificationType.INFO,
            NotificationType.WARN,
        ]
    ],
)
def test_notification_times_out(widget, mock_dispatch, mock_notifications_feature):
    assert widget.get_ref().get_child_revealed()
    sleep(1.2)
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=REMOVE_NOTIFICATION,
            payload=Attrs(
                id=0,
            ),
        )
    )

    # since we are mocking dispatch we have to manually fire the on_next
    mock_notifications_feature.on_next([])
    assert not widget.get_ref().get_child_revealed()


@pytest.mark.usefixtures("mock_notifications_feature")
@pytest.mark.parametrize(
    "notifications",
    [[Note(0, "foo", t, None)] for t in [NotificationType.ERROR]],
)
def test_notification_does_not_time_out(widget, mock_dispatch):
    assert widget.get_ref().get_child_revealed()
    sleep(1.2)
    mock_dispatch.assert_not_any_call(
        InstanceOf(Action) & Attrs(type=REMOVE_NOTIFICATION)
    )
    assert widget.get_ref().get_child_revealed()


@pytest.mark.parametrize(
    "notifications",
    [[Note(0, "foo", t, None)] for t in [NotificationType.WARN]],
)
def test_turns_off_timer(widget, mock_notifications_feature, mock_dispatch):
    mock_notifications_feature.on_next(
        [Note(1, "warning", NotificationType.ERROR, None)]
    )
    sleep(1.2)
    mock_dispatch.assert_not_any_call(
        InstanceOf(Action) & Attrs(type=REMOVE_NOTIFICATION)
    )
    assert widget.get_ref().get_child_revealed()


@pytest.mark.parametrize(
    "notifications",
    [[Note(0, "foo", t, None)] for t in [NotificationType.ERROR]],
)
def test_changes_styles(widget, mock_notifications_feature):
    container = widget.get_object("container")
    style = container.get_style_context()
    assert NotificationType.ERROR.value in style.list_classes()
    assert NotificationType.WARN.value not in style.list_classes()

    mock_notifications_feature.on_next(
        [Note(1, "warning", NotificationType.WARN, None)]
    )
    assert NotificationType.ERROR.value not in style.list_classes()
    assert NotificationType.WARN.value in style.list_classes()
