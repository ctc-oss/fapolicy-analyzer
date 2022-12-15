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

from unittest.mock import MagicMock

import context  # noqa: F401

from fapolicy_analyzer.ui.actions import Notification, NotificationType
from fapolicy_analyzer.ui.reducers.notification_reducer import (
    handle_add_notification,
    handle_remove_notification,
)


def test_handle_add_notification():
    result = handle_add_notification([], MagicMock(payload="foo"))
    assert list(result) == ["foo"]


def test_handle_remove_notification():
    state = [
        Notification(id=99, text=None, type=NotificationType.ERROR, category=None),
        Notification(id=100, text=None, type=NotificationType.ERROR, category=None),
    ]
    result = handle_remove_notification(
        state,
        MagicMock(payload=Notification(id=99, text=None, type=None, category=None)),
    )
    assert result == state[1:]
