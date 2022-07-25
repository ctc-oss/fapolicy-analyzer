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

import gi

try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources

from fapolicy_analyzer.ui.actions import NotificationType, remove_notification
from fapolicy_analyzer.ui.store import dispatch, get_notifications_feature
from fapolicy_analyzer.ui.ui_widget import UIConnectedWidget

gi.require_version("GtkSource", "3.0")
from gi.repository import Gio, Gtk  # isort: skip


class Notification(UIConnectedWidget):
    def __init__(self, timer_duration=10):
        super().__init__(
            get_notifications_feature(), on_next=self.on_next_notifications
        )
        self.message = self.get_object("message")
        self.container = self.get_object("container")
        self.closeBtn = self.get_object("closeBtn")
        self.timerDuration = timer_duration
        self.timer = None
        self.notification_id = None

        styleProvider = Gtk.CssProvider()
        with resources.path("fapolicy_analyzer.css", "notification.css") as path:
            styleProvider.load_from_file(Gio.File.new_for_path(path.as_posix()))

        self.style = self.container.get_style_context()
        self.style.add_provider(styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.closeBtn.get_style_context().add_provider(
            styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def __start_timer(self):
        self.timer = Timer(self.timerDuration, self.closeBtn.clicked)
        self.timer.start()

    def __stop_timer(self):
        self.timer.cancel()
        self.timer = None

    def on_next_notifications(self, notifications):
        first = next(iter(notifications), None)
        if first:
            message = first.text
            notificationType = first.type
            self.style.add_class(notificationType.value)
            self.message.set_label(message)
            self.notification_id = first.id
            self.get_ref().set_reveal_child(True)

            if notificationType not in [NotificationType.ERROR, NotificationType.WARN]:
                self.__start_timer()
        else:
            self.get_ref().set_reveal_child(False)
            self.notification_id = None

    def on_closeBtn_clicked(self, *args):
        if self.timer:
            self.__stop_timer()
        dispatch(remove_notification(self.notification_id))
