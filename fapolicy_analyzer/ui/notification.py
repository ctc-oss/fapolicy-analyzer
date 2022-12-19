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

from threading import Timer
from typing import Sequence

import gi

from fapolicy_analyzer.ui import get_resource
from fapolicy_analyzer.ui.actions import (
    Notification,
    NotificationType,
    remove_notification,
)
from fapolicy_analyzer.ui.store import dispatch, get_notifications_feature
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget

gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk  # isort: skip


class Notification(UIConnectedWidget):
    def __init__(self, timer_duration: int = 10):
        super().__init__(
            get_notifications_feature(), on_next=self.on_next_notifications
        )
        self.__message = self.get_object("message")
        self.__container = self.get_object("container")
        self.__closeBtn = self.get_object("closeBtn")
        self.timerDuration = timer_duration
        self.__timer = None
        self.__notification_id = None

        styleProvider = Gtk.CssProvider()
        styleProvider.load_from_data(get_resource("notification.css").encode())

        self.__style = self.__container.get_style_context()
        self.__style.add_provider(
            styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.__closeBtn.get_style_context().add_provider(
            styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def __start_timer(self):
        self.__timer = Timer(self.timerDuration, self.__closeBtn.clicked)
        self.__timer.start()

    def __stop_timer(self):
        if self.__timer:
            self.__timer.cancel()
            self.__timer = None

    def __set_notification_style(self, notification_type: NotificationType):
        # first remove old styles
        for t in NotificationType:
            self.__style.remove_class(t.value)

        self.__style.add_class(notification_type.value)

    def __create_notification(self, notification: Notification):
        message = notification.text
        notification_type = notification.type
        self.__set_notification_style(notification_type)
        self.__message.set_label(message)
        self.__notification_id = notification.id

    def on_next_notifications(self, notifications: Sequence[Notification]):
        first = next(iter(notifications), None)
        if first:
            # stop old timer
            self.__stop_timer()

            # create new notification
            self.__create_notification(first)
            self.get_ref().set_reveal_child(True)

            # start new timer if needed
            if first.type not in [NotificationType.ERROR]:
                self.__start_timer()
        else:
            self.get_ref().set_reveal_child(False)
            self.__notification_id = None

    def on_closeBtn_clicked(self, *args):
        self.__stop_timer()
        dispatch(remove_notification(self.__notification_id))
