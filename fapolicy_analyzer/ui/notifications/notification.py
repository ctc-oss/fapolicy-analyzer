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

from threading import Timer

import gi
from fapolicy_analyzer.ui import get_resource
from fapolicy_analyzer.ui.actions import NotificationType, remove_notification
from fapolicy_analyzer.ui.store import dispatch
from fapolicy_analyzer.ui.ui_widget import UIBuilderWidget

gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk  # isort: skip


class Notification(UIBuilderWidget):
    def __init__(
        self, id: int, type: NotificationType, message: str, duration: int = 10
    ):
        super().__init__()
        self.__id = id
        self.__message = self.get_object("message")
        self.__closeBtn = self.get_object("closeBtn")
        self.__duration = duration
        self.__timer = None

        self.__message.set_label(message)

        styleProvider = Gtk.CssProvider()
        styleProvider.load_from_data(get_resource("notification.css").encode())

        style = self.get_ref().get_style_context()
        style.add_provider(styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        style.add_class(type.value)
        self.__closeBtn.get_style_context().add_provider(
            styleProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        if type is not NotificationType.ERROR:
            self.__start_timer()

    def __start_timer(self):
        self.__timer = Timer(self.__duration, self.__closeBtn.clicked)
        self.__timer.start()

    def __stop_timer(self):
        self.__timer.cancel()
        self.__timer = None

    def on_closeBtn_clicked(self, *args):
        if self.__timer:
            self.__stop_timer()
        dispatch(remove_notification(self.__id))
