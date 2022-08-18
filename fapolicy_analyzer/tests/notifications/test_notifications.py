# Copyright Concurrent Technologies Corporation 2022
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
import gi
import pytest
from fapolicy_analyzer.ui.actions import Notification as Note
from fapolicy_analyzer.ui.actions import NotificationType
from fapolicy_analyzer.ui.notifications.notifications import Notifications
from rx.subject import Subject

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # isort: skip


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("fapolicy_analyzer.ui.notifications.dispatch")


@pytest.fixture
def mock_notifications_feature(mocker):
    notifications_feature_mock = Subject()
    mocker.patch(
        "fapolicy_analyzer.ui.notifications.notifications.get_notifications_feature",
        return_value=notifications_feature_mock,
    )
    yield notifications_feature_mock
    notifications_feature_mock.on_completed()


@pytest.fixture
def widget(mock_notifications_feature, notifications):
    widget = Notifications(display_limit=2)
    overlay = Gtk.Overlay()
    overlay.add_overlay(widget.get_ref())
    parent = Gtk.Window()
    parent.add(overlay)
    mock_notifications_feature.on_next(notifications)
    return widget


@pytest.mark.usefixtures("mock_notifications_feature")
@pytest.mark.parametrize(
    "notifications, notification_type",
    [([Note(0, "foo", t)], t) for t in list(NotificationType)],
)
def test_shows_notification(widget, notification_type):
    assert widget.get_ref().get_child_revealed()
    notifications = widget.get_ref().get_child().get_children()
    assert len(notifications) == 1
    notification = next(iter(notifications))
    label = notification.get_children()[0]

    assert label.get_label() == "foo"
    assert notification.get_style_context().has_class(notification_type.name.lower())


@pytest.mark.usefixtures("mock_notifications_feature")
@pytest.mark.parametrize(
    "notifications",
    [
        (
            [
                Note(0, "note 1", NotificationType.ERROR),
                Note(1, "note 2", NotificationType.WARN),
            ]
        )
    ],
)
def test_limits_notifications(widget):
    assert widget.get_ref().get_child_revealed()
    notifications = widget.get_ref().get_child().get_children()
    assert len(notifications) == 2


@pytest.mark.usefixtures("mock_notifications_feature")
@pytest.mark.parametrize(
    "notifications",
    [
        (
            [
                Note(0, "note 1", NotificationType.ERROR),
                Note(1, "note 2", NotificationType.WARN),
                Note(1, "note 2", NotificationType.INFO),
            ]
        )
    ],
)
def test_shows_multiple_notifications(widget):
    assert widget.get_ref().get_child_revealed()
    notifications = widget.get_ref().get_child().get_children()
    assert len(notifications) == 2


@pytest.mark.parametrize(
    "notifications",
    [([Note(0, "note 1", NotificationType.ERROR)])],
)
def test_hides_when_no_notifications(widget, mock_notifications_feature):
    assert widget.get_ref().get_child_revealed()
    mock_notifications_feature.on_next([])
    assert not widget.get_ref().get_child_revealed()
