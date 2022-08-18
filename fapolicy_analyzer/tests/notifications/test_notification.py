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

import pytest
from callee import InstanceOf
from callee.attributes import Attrs
from fapolicy_analyzer.redux import Action
from fapolicy_analyzer.ui.actions import REMOVE_NOTIFICATION, NotificationType
from fapolicy_analyzer.ui.notifications.notification import Notification


@pytest.fixture()
def mock_dispatch(mocker):
    return mocker.patch("fapolicy_analyzer.ui.notifications.notification.dispatch")


@pytest.fixture
def widget(id, type, message):
    return Notification(id, type, message, duration=1)


@pytest.mark.parametrize(
    "id, type, message, expected_type, expected_message",
    [
        (0, t, f"{t.name} message", t, f"{t.name} message")
        for t in list(NotificationType)
    ],
)
def test_creates_widget(widget, expected_type, expected_message):
    assert widget.get_object("message").get_label() == expected_message
    assert widget.get_ref().get_style_context().has_class(expected_type.name.lower())


@pytest.mark.parametrize(
    "id, type, message, expected_id",
    [(idx, t, "foo", idx) for idx, t in enumerate(NotificationType)],
)
def test_closes_notification(widget, mock_dispatch, expected_id):
    widget.get_object("closeBtn").clicked()
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(type=REMOVE_NOTIFICATION, payload=Attrs(id=expected_id))
    )


@pytest.mark.usefixtures("widget")
@pytest.mark.parametrize(
    "id, type, message, expected_id",
    [
        (idx, t, "foo", idx)
        for idx, t in enumerate(
            [NotificationType.SUCCESS, NotificationType.INFO, NotificationType.WARN]
        )
    ],
)
def test_notification_times_out(mock_dispatch, expected_id):
    sleep(1.2)
    mock_dispatch.assert_called_with(
        InstanceOf(Action)
        & Attrs(
            type=REMOVE_NOTIFICATION,
            payload=Attrs(
                id=expected_id,
            ),
        )
    )


@pytest.mark.usefixtures("widget")
@pytest.mark.parametrize(
    "id, type, message",
    [(0, NotificationType.ERROR, "foo")],
)
def test_notification_does_not_time_out(mock_dispatch):
    sleep(1.2)
    mock_dispatch.assert_not_any_call(
        InstanceOf(Action) & Attrs(type=REMOVE_NOTIFICATION)
    )
