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

import gi
from fapolicy_analyzer.ui.notifications.notification import Notification
from fapolicy_analyzer.ui.store import get_notifications_feature
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget

gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk  # isort: skip


class Notifications(UIConnectedWidget):
    def __init__(self, display_limit: int = 5, duration: int = 10):
        super().__init__(
            get_notifications_feature(), on_next=self.on_next_notifications
        )
        self.__display_limit = display_limit
        self.__duration = duration
        self.__ref = self.get_ref()
        self.__displayed_notifications = []

    def __build_notifications(self, notifications):
        container = Gtk.Box(
            homogeneous=True, spacing=0, orientation=Gtk.Orientation.VERTICAL
        )
        for n in notifications:
            notification = Notification(n.id, n.type, n.text, self.__duration)
            container.pack_end(notification.get_ref(), True, True, 0)
        container.show_all()
        return container

    def on_next_notifications(self, notifications):
        notifications_to_display = notifications[: self.__display_limit]
        if self.__displayed_notifications != notifications_to_display:
            self.__displayed_notifications = notifications_to_display
            self.__ref.get_child().destroy()
            self.__ref.add(self.__build_notifications(notifications_to_display))
            self.get_ref().set_reveal_child(notifications_to_display)
